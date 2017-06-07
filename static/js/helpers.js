/**
 * Created by kecorbin on 6/6/17.
 */

function showProgress(form, url) {
    // displays progress bar until page reloads
    $('#myPleaseWait').modal('show')

}
function showmodal(url) {
    // Show modal for gathering credentials
    $('#credentials').modal('show');

}

function submitCreds(url) {
    // called when credentials form is submitted
    var form = $(this)
    form.submit()
    $('#credentials').modal('hide')
    showProgress(form, url)

}

// prompt for confirmation when deleting a delta
function deleteCR(url) {

    if(confirm("Are you sure?")) {
        $.ajax({
            url: url,
            type: 'DELETE',
            success: function() {
                window.location.href = '/'
            }
        })
    }
}
