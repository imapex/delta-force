/**
 * Created by kecorbin on 6/6/17.
 */

function showProgress(form, url) {
    console.log('showing progress')
    $('#myPleaseWait').modal('show')
    //form.submit()
}
function showmodal(url) {
    // Show modal, then submit form
    $('#credentials').modal('show');

}

function submitCreds(url) {
    console.log('submitting creds')
    console.log(url)
    var form = $(this)
    form.submit()
    $('#credentials').modal('hide')
    showProgress(form, url)

}

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
