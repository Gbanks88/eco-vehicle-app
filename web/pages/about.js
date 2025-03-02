import Layout from '../components/Layout';

export default function About() {
  return (
    <Layout>
      <div className="bg-white">
        <main className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            <div className="lg:col-span-8">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
                About Eco Vehicle
              </h1>
              <p className="mt-6 text-xl text-gray-500">
                We are dedicated to promoting sustainable transportation solutions and helping vehicle owners make environmentally conscious decisions.
              </p>

              <section className="mt-12">
                <h2 className="text-2xl font-bold text-gray-900">Our Mission</h2>
                <p className="mt-4 text-lg text-gray-500">
                  To accelerate the world's transition to sustainable transportation by providing comprehensive resources, tools, and products that help vehicle owners reduce their environmental impact.
                </p>
              </section>

              <section className="mt-12">
                <h2 className="text-2xl font-bold text-gray-900">What We Do</h2>
                <div className="mt-4 space-y-6">
                  <p className="text-lg text-gray-500">
                    We offer a curated selection of eco-friendly vehicle products, educational resources, and interactive tools to help you:
                  </p>
                  <ul className="list-disc list-inside text-lg text-gray-500 space-y-3">
                    <li>Reduce your vehicle's environmental impact</li>
                    <li>Save money on fuel and maintenance</li>
                    <li>Make informed decisions about sustainable transportation</li>
                    <li>Connect with other eco-conscious vehicle owners</li>
                  </ul>
                </div>
              </section>

              <section className="mt-12">
                <h2 className="text-2xl font-bold text-gray-900">Our Values</h2>
                <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Sustainability</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We prioritize environmental impact in everything we do.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Education</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We believe in empowering through knowledge.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Innovation</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We embrace new technologies and solutions.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Community</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We foster connections between eco-conscious individuals.
                    </p>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </main>
      </div>
    </Layout>
  );
}
