// Handling user consent

// Prevent default enter key form submisssion unless user gives consent
$(function() {
    $('#id_email').on('keydown', function(event) {
        var userConsent = $('#user-consent');
        var hasConsent = userConsent.prop('checked');
        if ((event.key == 'Enter') && (!hasConsent)) {
            event.preventDefault();

            // Create and display alert
            let termsUrl = userConsent.attr('termsurl');
            let policyUrl = userConsent.attr('policyurl');
            let htmlAlert = `<div id="consent-reminder" class="alert alert-info alert-dismissible" role="alert">
                  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                  </button>
                  Please acknowledge that you have read and agree to our <a href="${termsUrl}" class="alert-link" target="_blank">Terms of Use</a> and <a href="${policyUrl}" class="alert-link" target="_blank">Privacy Policy</a>.
                </div>`;
            $('header.header').prepend(htmlAlert);
        }
    });
})

// Toggle submit button based on consent checkbox
$(function() {
    $('#user-consent').click(function() {
        let = isChecked = this.checked;
        $('#submit-btn').attr('disabled', !isChecked);
        $('#user-consent').prop('checked', isChecked);
    });
})
