import stripe

stripe.api_key = 'sk_test_51Q4fHlEnEVSBT8En6GJbcTL7O6vGqBJhRna2SNvQJbaF1peU1Mx2eeirZTWFufTwcVl6bbG08saRXD9uG5bUXZT400Poc4UFGZ'

try:
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Test produit',
                },
                'unit_amount': 1000,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://httpbin.org/post',
        cancel_url='https://httpbin.org/post',
        metadata={'client_reference_id': 'test_reference_id'},  # Utilisation d'une valeur fixe pour tester
    )

    print(f'Session ID: {session.id}')
    print(f'Metadata: {session.metadata}')

except stripe.error.StripeError as e:
    print(f'Erreur Stripe: {str(e)}')
