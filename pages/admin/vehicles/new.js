import Head from 'next/head';
import AdminLayout from '../../../components/admin/Layout';
import VehicleForm from '../../../components/admin/VehicleForm';

export default function NewVehicle() {
  return (
    <AdminLayout>
      <Head>
        <title>New Vehicle - Eco Vehicle Admin</title>
      </Head>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
        <VehicleForm mode="create" />
      </div>
    </AdminLayout>
  );
}
