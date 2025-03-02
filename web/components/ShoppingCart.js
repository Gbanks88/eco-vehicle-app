import { useState, useEffect } from 'react';
import Image from 'next/image';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

export default function ShoppingCart({ isOpen, setIsOpen }) {
  const [cartItems, setCartItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load cart items from localStorage
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      setCartItems(JSON.parse(savedCart));
    }
  }, []);

  const updateQuantity = (productId, newQuantity) => {
    const updatedCart = cartItems.map(item =>
      item.productId === productId
        ? { ...item, quantity: Math.max(0, newQuantity) }
        : item
    ).filter(item => item.quantity > 0);

    setCartItems(updatedCart);
    localStorage.setItem('cart', JSON.stringify(updatedCart));
  };

  const removeItem = (productId) => {
    const updatedCart = cartItems.filter(item => item.productId !== productId);
    setCartItems(updatedCart);
    localStorage.setItem('cart', JSON.stringify(updatedCart));
  };

  const subtotal = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const handleCheckout = async () => {
    try {
      setIsLoading(true);

      // Create order
      const orderRes = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: cartItems,
          amount: subtotal,
        }),
      });

      if (!orderRes.ok) throw new Error('Failed to create order');
      const { _id: orderId } = await orderRes.json();

      // Create payment intent
      const paymentRes = await fetch('/api/payments/create-payment-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: subtotal * 100, // Convert to cents for Stripe
          orderId,
        }),
      });

      if (!paymentRes.ok) throw new Error('Failed to create payment intent');
      const { clientSecret } = await paymentRes.json();

      // Redirect to Stripe checkout
      const stripe = await stripePromise;
      const { error } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement),
          billing_details: {
            name: 'Customer Name', // You should get this from a form
          },
        },
      });

      if (error) {
        throw new Error(error.message);
      } else {
        // Clear cart after successful payment
        setCartItems([]);
        localStorage.removeItem('cart');
        setIsOpen(false);
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to process checkout. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`fixed inset-0 overflow-hidden ${isOpen ? 'z-50' : 'hidden'}`}>
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setIsOpen(false)} />
        
        <div className="fixed inset-y-0 right-0 pl-10 max-w-full flex">
          <div className="w-screen max-w-md">
            <div className="h-full flex flex-col bg-white shadow-xl overflow-y-scroll">
              <div className="flex-1 py-6 overflow-y-auto px-4 sm:px-6">
                <div className="flex items-start justify-between">
                  <h2 className="text-lg font-medium text-gray-900">Shopping Cart</h2>
                  <div className="ml-3 h-7 flex items-center">
                    <button
                      type="button"
                      className="-m-2 p-2 text-gray-400 hover:text-gray-500"
                      onClick={() => setIsOpen(false)}
                    >
                      <span className="sr-only">Close panel</span>
                      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div className="mt-8">
                  <div className="flow-root">
                    <ul className="-my-6 divide-y divide-gray-200">
                      {cartItems.map((item) => (
                        <li key={item.productId} className="py-6 flex">
                          <div className="relative flex-shrink-0 w-24 h-24 rounded-md overflow-hidden">
                            <Image
                              src={item.imageUrl || '/placeholder-vehicle.jpg'}
                              alt={item.name}
                              layout="fill"
                              objectFit="cover"
                            />
                          </div>

                          <div className="ml-4 flex-1 flex flex-col">
                            <div>
                              <div className="flex justify-between text-base font-medium text-gray-900">
                                <h3>{item.name}</h3>
                                <p className="ml-4">${(item.price * item.quantity).toLocaleString()}</p>
                              </div>
                            </div>
                            <div className="flex-1 flex items-end justify-between text-sm">
                              <div className="flex items-center">
                                <button
                                  onClick={() => updateQuantity(item.productId, item.quantity - 1)}
                                  className="text-gray-500 hover:text-gray-700"
                                >
                                  -
                                </button>
                                <span className="mx-2 text-gray-700">{item.quantity}</span>
                                <button
                                  onClick={() => updateQuantity(item.productId, item.quantity + 1)}
                                  className="text-gray-500 hover:text-gray-700"
                                >
                                  +
                                </button>
                              </div>
                              <button
                                type="button"
                                onClick={() => removeItem(item.productId)}
                                className="font-medium text-blue-600 hover:text-blue-500"
                              >
                                Remove
                              </button>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 py-6 px-4 sm:px-6">
                <div className="flex justify-between text-base font-medium text-gray-900">
                  <p>Subtotal</p>
                  <p>${subtotal.toLocaleString()}</p>
                </div>
                <p className="mt-0.5 text-sm text-gray-500">Shipping and taxes calculated at checkout.</p>
                <div className="mt-6">
                  <button
                    onClick={handleCheckout}
                    disabled={cartItems.length === 0 || isLoading}
                    className={`w-full flex justify-center items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-blue-600 hover:bg-blue-700 ${
                      (cartItems.length === 0 || isLoading) && 'opacity-50 cursor-not-allowed'
                    }`}
                  >
                    {isLoading ? 'Processing...' : 'Checkout'}
                  </button>
                </div>
                <div className="mt-6 flex justify-center text-sm text-center text-gray-500">
                  <p>
                    or{' '}
                    <button
                      type="button"
                      className="text-blue-600 font-medium hover:text-blue-500"
                      onClick={() => setIsOpen(false)}
                    >
                      Continue Shopping<span aria-hidden="true"> →</span>
                    </button>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
