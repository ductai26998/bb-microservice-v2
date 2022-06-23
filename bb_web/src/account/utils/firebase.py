from ...core.firebase import check_fcm_token_valid


def clean_up_user_fcm_tokens(user):
    fcm_tokens = user.fcm_tokens
    valid_fcm_tokens = []
    for fcm_token in fcm_tokens:
        if check_fcm_token_valid(fcm_token):
            valid_fcm_tokens.append(fcm_token)
    user.store_value_in_private_metadata({"fcm_tokens": valid_fcm_tokens})
    user.save(update_fields=("private_metadata",))
    return fcm_tokens != valid_fcm_tokens
