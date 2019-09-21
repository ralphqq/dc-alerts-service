"""
Constants, functions, and classes that don't fit in other modules.
"""

# Emojis to be used
emojis = {
    'water': '\U0001F6B0',          # potable water
    'power': '\U0001F50C',          # electric plug
    'ict': '\U0001F4E1',            # satellite antenna
    'welcome': '\U0001F91D',        # handshake
    'goodbye': '\U0001F44B',        # waving hand
    'reminder': '\U0001F514',       # bell
    'default': '\U0001F4E2',        # loudspeakers
}


# Filenames of email templates
# and subject lines associated with 
# each transactional message type
message_components = {
    'confirm': {
        'template': 'email_alerts/confirmation_email.html',
        'subject': f"{emojis['reminder']} Please confirm your email address",
        'target_view': 'verify_email'
    },
    'goodbye': {
        'template': 'email_alerts/goodbye_email.html',
        'subject': f"{emojis['goodbye']} You have successfully unsubscribed",
        'target_view': None
    },
    'optout': {
        'template': 'email_alerts/optout_email.html',
        'subject': f"{emojis['reminder']} Unsubscribe from our mailing list",
        'target_view': 'unsubscribe_user'
    },
    'welcome': {
        'template': 'email_alerts/welcome_email.html',
        'subject': f"{emojis['welcome']} Welcome to DVO Alerts!",
        'target_view': 'unsubscribe_user'
    }
}
