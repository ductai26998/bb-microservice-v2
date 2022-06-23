import firebase_admin
from firebase_admin import credentials, messaging

CREDENTIALS_FIREBASE_PATH = "base/services/firebase-adminsdk.json"

# def get_user_on_firestore(user):
#     if not user.firebase_uid:
#         return None
#     firebase_initialize_app()
#     db = firestore.client()
#     doc_ref = db.collection("Users").document(user.firebase_uid)
#     doc = doc_ref.get()
#     if doc.exists:
#         return doc.to_dict()
#     return None


def firebase_initialize_app():
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(CREDENTIALS_FIREBASE_PATH)
        firebase_admin.initialize_app(cred)


# def get_badge_number(user):
#     user_on_firestore = get_user_on_firestore(user)
#     total_unread_chat = (
#         user_on_firestore.get("totalUnreadChat", 0) if user_on_firestore else 0
#     )
#     total_unread_other = user.concat_notifications.unread().count()
#     return total_unread_chat + total_unread_other


def send_notify_multiple_recipient(
    recipients, message_title: str, message_body: str, data_message=None, **kwargs
):
    firebase_initialize_app()
    # Create a list containing up to 500 registration tokens.
    # These registration tokens come from the client FCM SDKs.
    notification = messaging.Notification(
        title=message_title, body=message_body, image=kwargs.get("image", "")
    )
    success_ids = []
    failure_count = 0
    for recipient in recipients:
        registration_tokens = recipient.fcm_tokens

        if registration_tokens:
            # badge_number = get_badge_number(recipient)
            android = messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    # priority="high", default_sound=True, notification_count=badge_number
                    priority="high",
                    default_sound=True,
                )
            )
            apns = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        mutable_content=True
                        # sound="default", badge=None, mutable_content=True
                    )
                ),
                headers={
                    "apns-priority": "10",
                },
            )
            try:
                message = messaging.MulticastMessage(
                    tokens=registration_tokens,
                    data=data_message,
                    notification=notification,
                    apns=apns,
                    android=android,
                )
                batch_response = messaging.send_multicast(message)

                failure_count += batch_response.failure_count
            except Exception as e:
                batch_response = None
                print(">>>>>> Error send push notification: ", e)
    return (success_ids, failure_count)


def check_fcm_token_valid(fcm_token):
    firebase_initialize_app()
    message = messaging.Message(
        token=fcm_token,
    )
    try:
        messaging.send(message, dry_run=True)
    except firebase_admin.exceptions.FirebaseError as e:
        if e.code == "NOT_FOUND":
            return False
    return True
