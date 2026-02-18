from modules.webhooks.paystack import PaystackWebhookHandler
# from modules.webhooks.flutterwave import FlutterwaveWebhookHandler



WEBHOOK_PROVIDERS = {
    "paystack": PaystackWebhookHandler(),
    # "flutterwave": FlutterwaveWebhookHandler(),
}