import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import AdminLayout from '../../../../components/admin/Layout';
import VehicleForm from '../../../../components/admin/VehicleForm';

export default function EditVehicle() {
  const router = useRouter();
  const { id } = router.query;
  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchVehicle();
    }
  }, [id]);

  const fetchVehicle = async () => {
    try {
      const response = await fetch(`/api/vehicles/${id}`);
      if (!response.ok) throw new Error('Failed to fetch vehicle');
      const data = await response.json();
      setVehicle(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <AdminLayout>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
          <div className="bg-red-50 p-4 rounded-md">
            <p className="text-red-700">Error: {error}</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

  if (loading) {
    return (
      <AdminLayout>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
          <p>Loading...</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <Head>
        <title>Edit Vehicle - Eco Vehicle Admin</title>
      </Head>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
        <VehicleForm vehicle={vehicle} mode="edit" />
      </div>
    </AdminLayout>
  );
}
