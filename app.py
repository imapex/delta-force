import os
from flask import Flask, render_template, request, flash, redirect, Response
# from difflib import HtmlDiff
from utils import HtmlDiffer
from flask_sqlalchemy import SQLAlchemy
from wtforms_alchemy import ModelForm
from lxml import etree
from commands import run_commands
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'change.db')
db = SQLAlchemy(app)


def logo():
    return "/static/img/deltaforce.png"


class Change(db.Model):
    __tablename__ = 'Changes'
    cr = db.Column(db.String, primary_key=True)
    verification_commands = db.Column(db.Text)
    verified_hosts = db.Column(db.Text)
    default_output = "Not collected yet" + ("." * 103)
    before = db.Column(db.Text, default=default_output, nullable=True)
    after = db.Column(db.Text, default=default_output, nullable=True)

    def __init__(self, cr, verification_commands, verified_hosts):
        self.cr = cr
        self.verification_commands = verification_commands
        self.verified_hosts = verified_hosts

    def __repr__(self):
        return "<CR {}>".format(self.cr)


class ChangeForm(ModelForm):
    class Meta:
        include = ['cr', 'verified_hosts', 'verification_commands']
        exclude = ['before', 'after']
        model = Change


@app.route('/', methods=["GET", "POST"])
def index():
    form = ChangeForm(request.form)
    change_records = Change.query.all()
    if form.validate() and request.method == "POST":
        cr = Change(form.cr.data, form.verification_commands.data, form.verified_hosts.data)
        db.session.add(cr)
        db.session.commit()
        change_records = Change.query.all()
        return render_template('index.html', change_records=change_records, form=form, logo=logo())

    return render_template('index.html', change_records=change_records, form=form, logo=logo())


@app.route('/cr/<string:id>', methods=["GET", "DELETE"])
def detail(id):
    show_command = request.args.get("show_command", None)
    show_device = request.args.get("show_device", None)
    print show_command, show_device
    obj = Change.query.get_or_404(id)

    if request.method == "DELETE":
        db.session.delete(obj)
        db.session.commit()
        return Response(status=200)


    # if we can load up valid xml, we'll give a better UI
    try:
        before_xml = etree.fromstring(obj.before)
        after_xml = etree.fromstring(obj.after)

    except etree.XMLSyntaxError as e:
        before_xml, after_xml = None, None
        flash("Could not detect valid XML.  This is likely because you haven't taken a full snapshot yet Details: {}".format(e), category="alert-warning")

    change_records = Change.query.all()
    before_lines = obj.before.split('\n')
    before_collected = len(before_lines) > 2
    after_lines = obj.after.split('\n')
    commands = [command for command in obj.verification_commands.split('\n') if command.strip() != '']
    hosts = [host for host in obj.verified_hosts.split('\n') if host.strip() != '']
    diff = HtmlDiffer(wrapcolumn=120)
    table = diff.make_table(before_lines, after_lines)

    if before_xml and after_xml is not None:
        # Generate advanced view

        if show_command is not None:
            xpath_query = "//command[@cmd='{} ']/text()".format(show_command)
            print xpath_query
            before_command_lines = before_xml.xpath(xpath_query)[0].split('\n')
            after_command_lines = after_xml.xpath(xpath_query)[0].split('\n')
            print before_command_lines, after_command_lines
            table = diff.make_table(before_command_lines, after_command_lines)

        return render_template('advanced.html',
                               hosts=hosts,
                               change_records=change_records,
                               commands=commands,
                               before_collected=before_collected,
                               change=obj,
                               table=table,
                               logo=logo())

    else:
        # Return standard view
        return render_template('detail.html',
                               hosts=hosts,
                               change_records=change_records,
                               commands=commands,
                               before_collected=before_collected,
                               change=obj,
                               table=table,
                               logo=logo())


@app.route('/cr/<string:id>/<string:snap>', methods=["POST"])
def capture_output(id, snap):
    """
     Capture the registered show commands for a CR
    :param id: CR number
    :param snap: specify which snapshot (before/after)
    :return:
    """
    # All posts should come to snap, if a before snap already exists, we will assume it's after

    if snap not in ['snap']:
        return Response(status=404)
    obj = Change.query.get_or_404(id)

    # baseline exists if more than the default string is set...
    if len(obj.before) > 120:
        snap_type = 'after'
    else:
        snap_type = 'before'

    host_list = [host for host in obj.verified_hosts.split('\n') if host.strip() != '']
    command_list = [command for command in obj.verification_commands.split('\n') if command.strip() != '']

    # Get login credentials from modal form
    user = request.form.get('username')
    pw = request.form.get('password')

    try:
        output = run_commands(host_list, user, pw, command_list)

        setattr(obj, snap_type, output)

        db.session.commit()
        flash('Successfully Gathered {} Commands'.format(snap_type), category="alert-success")
    except Exception as e:
        flash('Error gathering commands.. {}'.format(e), category="alert-danger")
    return redirect('/cr/{}'.format(obj.cr))


if __name__ == '__main__':
    app.secret_key = 'sdflkjsdflkjsdflkjsdf'
    db.create_all()
    app.run(debug=True)
