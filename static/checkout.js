// This is your test publishable API key.
const stripe = Stripe("pk_test_51PIN3l2M890h7uzkQ64lmsTYkVrW8Ey1hK5ixLqnmuELmfZSN8Rs4uEDxwkwGm22IQTF9zt3FSC4Q0AsUbUgZjVI005UpOrfLT");

initialize();

// Create a Checkout Session
async function initialize() {
  const fetchClientSecret = async () => {
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });
    const { clientSecret } = await response.json();
    return clientSecret;
  };

  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}