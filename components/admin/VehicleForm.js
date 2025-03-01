import { useState } from 'react';
import { useRouter } from 'next/router';

export default function VehicleForm({ vehicle = {}, mode = 'create' }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: vehicle.name || '',
    category: vehicle.category || '',
    price: vehicle.price || '',
    image: vehicle.image || '',
    specs: {
      range: vehicle.specs?.range || '',
      acceleration: vehicle.specs?.acceleration || '',
      topSpeed: vehicle.specs?.topSpeed || '',
      power: vehicle.specs?.power || ''
    },
    features: vehicle.features || [],
    colors: vehicle.colors || [],
    availability: {
      status: vehicle.availability?.status || 'available',
      date: vehicle.availability?.date || ''
    }
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleFeatureChange = (e) => {
    const features = e.target.value.split(',').map(f => f.trim());
    setFormData(prev => ({
      ...prev,
      features
    }));
  };

  const handleColorChange = (e) => {
    const colors = e.target.value.split(',').map(c => ({
      name: c.trim(),
      hex: '#000000' // Default color, you might want to add a color picker
    }));
    setFormData(prev => ({
      ...prev,
      colors
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const url = mode === 'create' ? '/api/vehicles' : `/api/vehicles/${vehicle.id}`;
      const method = mode === 'create' ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to save vehicle');
      }

      router.push('/admin/vehicles');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 divide-y divide-gray-200">
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      <div className="space-y-8 divide-y divide-gray-200">
        <div>
          <div>
            <h3 className="text-lg font-medium leading-6 text-gray-900">
              {mode === 'create' ? 'New Vehicle' : 'Edit Vehicle'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Fill in the details below to {mode === 'create' ? 'create' : 'update'} a vehicle.
            </p>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-4">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  name="name"
                  id="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  required
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                Category
              </label>
              <div className="mt-1">
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  required
                >
                  <option value="">Select a category</option>
                  <option value="sedan">Sedan</option>
                  <option value="suv">SUV</option>
                  <option value="sports">Sports</option>
                  <option value="luxury">Luxury</option>
                </select>
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="price" className="block text-sm font-medium text-gray-700">
                Price
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  name="price"
                  id="price"
                  value={formData.price}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  required
                />
              </div>
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="image" className="block text-sm font-medium text-gray-700">
                Image URL
              </label>
              <div className="mt-1">
                <input
                  type="url"
                  name="image"
                  id="image"
                  value={formData.image}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  required
                />
              </div>
            </div>

            {/* Specifications */}
            <div className="sm:col-span-6">
              <h4 className="text-sm font-medium text-gray-900">Specifications</h4>
              <div className="mt-2 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-3">
                  <label htmlFor="specs.range" className="block text-sm font-medium text-gray-700">
                    Range (miles)
                  </label>
                  <input
                    type="number"
                    name="specs.range"
                    id="specs.range"
                    value={formData.specs.range}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  />
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="specs.acceleration" className="block text-sm font-medium text-gray-700">
                    Acceleration (0-60 mph)
                  </label>
                  <input
                    type="text"
                    name="specs.acceleration"
                    id="specs.acceleration"
                    value={formData.specs.acceleration}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  />
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="specs.topSpeed" className="block text-sm font-medium text-gray-700">
                    Top Speed (mph)
                  </label>
                  <input
                    type="number"
                    name="specs.topSpeed"
                    id="specs.topSpeed"
                    value={formData.specs.topSpeed}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  />
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="specs.power" className="block text-sm font-medium text-gray-700">
                    Power (hp)
                  </label>
                  <input
                    type="number"
                    name="specs.power"
                    id="specs.power"
                    value={formData.specs.power}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="features" className="block text-sm font-medium text-gray-700">
                Features (comma-separated)
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  name="features"
                  id="features"
                  value={formData.features.join(', ')}
                  onChange={handleFeatureChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                />
              </div>
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="colors" className="block text-sm font-medium text-gray-700">
                Available Colors (comma-separated)
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  name="colors"
                  id="colors"
                  value={formData.colors.map(c => c.name).join(', ')}
                  onChange={handleColorChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="availability.status" className="block text-sm font-medium text-gray-700">
                Availability Status
              </label>
              <div className="mt-1">
                <select
                  id="availability.status"
                  name="availability.status"
                  value={formData.availability.status}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                >
                  <option value="available">Available</option>
                  <option value="coming_soon">Coming Soon</option>
                  <option value="sold_out">Sold Out</option>
                </select>
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="availability.date" className="block text-sm font-medium text-gray-700">
                Availability Date
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  name="availability.date"
                  id="availability.date"
                  value={formData.availability.date}
                  onChange={handleChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-5">
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className={`ml-3 inline-flex justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm ${
              loading
                ? 'bg-green-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
            }`}
          >
            {loading ? 'Saving...' : mode === 'create' ? 'Create Vehicle' : 'Update Vehicle'}
          </button>
        </div>
      </div>
    </form>
  );
}
