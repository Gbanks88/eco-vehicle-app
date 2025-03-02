import { getSession } from 'next-auth/react';

export async function requireAuth(context, allowedRoles = ['admin']) {
  const session = await getSession(context);

  if (!session) {
    return {
      redirect: {
        destination: '/auth/signin',
        permanent: false,
      },
    };
  }

  if (!allowedRoles.includes(session.user.role)) {
    return {
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }

  return {
    props: { session }
  };
}
