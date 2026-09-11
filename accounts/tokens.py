from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

def make_activation_token(user):
    signer = TimestampSigner(salt="crowdfunding-account-activation")
    return signer.sign_object({"user_id": user.pk})

def get_user_from_activation_token(token):
    signer = TimestampSigner(salt="crowdfunding-account-activation")
    try:
        data = signer.unsign_object(token, max_age=24 * 60 * 60)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None
