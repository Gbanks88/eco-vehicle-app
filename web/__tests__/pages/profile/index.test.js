import { render } from '@testing-library/react';
import { screen, fireEvent, waitFor } from '@testing-library/dom';
import { useSession } from 'next-auth/react';
import Profile from '../../../pages/profile';

// Mock next-auth and fetch
jest.mock('next-auth/react');
global.fetch = jest.fn();

describe('Profile Page', () => {
  const mockProfile = {
    name: 'John Doe',
    email: 'john@example.com',
    createdAt: '2025-01-01T00:00:00.000Z',
    newsletterSubscribed: true,
  };

  const mockOrders = [
    {
      _id: '1',
      createdAt: '2025-02-01T00:00:00.000Z',
      amount: 1000,
      status: 'paid',
    },
  ];

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Mock successful authentication
    useSession.mockReturnValue({
      data: { user: { id: '123', name: 'John Doe', email: 'john@example.com' } },
      status: 'authenticated',
    });

    // Mock successful API responses
    fetch.mockImplementation((url) => {
      if (url === '/api/users/profile') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProfile),
        });
      }
      if (url === '/api/orders') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockOrders),
        });
      }
      return Promise.reject(new Error('Not found'));
    });
  });

  it('renders loading state initially', () => {
    useSession.mockReturnValueOnce({
      data: null,
      status: 'loading',
    });

    render(<Profile />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('redirects to sign in when not authenticated', () => {
    useSession.mockReturnValueOnce({
      data: null,
      status: 'unauthenticated',
    });

    const mockPush = jest.fn();
    jest.spyOn(require('next/router'), 'useRouter').mockImplementation(() => ({
      push: mockPush,
    }));

    render(<Profile />);
    expect(mockPush).toHaveBeenCalledWith('/auth/signin');
  });

  it('displays user profile information', async () => {
    render(<Profile />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('2025-01-01')).toBeInTheDocument();
    });
  });

  it('displays order history', async () => {
    render(<Profile />);

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument(); // Order ID
      expect(screen.getByText('2025-02-01')).toBeInTheDocument(); // Order date
      expect(screen.getByText('$1,000')).toBeInTheDocument(); // Order amount
      expect(screen.getByText('paid')).toBeInTheDocument(); // Order status
    });
  });

  it('handles newsletter subscription toggle', async () => {
    render(<Profile />);

    const checkbox = await waitFor(() => 
      screen.getByRole('checkbox', { name: /receive updates/i })
    );

    expect(checkbox).toBeChecked();

    // Mock the API call for updating newsletter preferences
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ message: 'Newsletter preferences updated successfully' }),
      })
    );

    fireEvent.click(checkbox);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/users/newsletter-preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subscribed: false }),
      });
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock failed API responses
    fetch.mockImplementation(() => 
      Promise.reject(new Error('API Error'))
    );

    render(<Profile />);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch profile/i)).toBeInTheDocument();
    });
  });
});
