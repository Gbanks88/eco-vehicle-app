import Head from 'next/head';
import Layout from '../components/Layout';

const AboutUs = () => {
  return (
    <Layout>
      <Head>
        <title>About Us - Creating Greatness For Foundation (CG4F)</title>
        <meta name="description" content="Learn about CG4F's mission to foster digital transformation and innovation for a sustainable future" />
      </Head>

      <main className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Creating Greatness For Foundation (CG4F)
          </h1>
        </div>

        <div className="prose prose-lg max-w-4xl mx-auto">
          {/* Mission */}
          <section className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 mb-6">Mission</h2>
            <p className="text-gray-700 mb-6">
              At CG4F, our mission is to foster digital transformation and innovation by leveraging emerging 
              technologies to create a sustainable and equitable future. We are committed to driving 
              progress in the fintech ecosystem, promoting advancements in artificial intelligence, blockchain, 
              IoT, and other cutting-edge fields while addressing the pressing challenges of climate change 
              and environmental sustainability.
            </p>
          </section>

          {/* Values */}
          <section className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 mb-6">Values</h2>
            <ul className="space-y-4 text-gray-700">
              <li>
                <strong className="text-gray-900">Innovation:</strong> We embrace and drive technological innovations that pave the way for a smarter, more connected world.
              </li>
              <li>
                <strong className="text-gray-900">Sustainability:</strong> We prioritize eco-friendly practices, renewable energy, and sustainable development to protect our planet for future generations.
              </li>
              <li>
                <strong className="text-gray-900">Collaboration:</strong> We work together with tech startups, researchers, and industry leaders to build a robust tech ecosystem.
              </li>
              <li>
                <strong className="text-gray-900">Equity:</strong> We advocate for climate justice and equitable access to digital resources and opportunities.
              </li>
              <li>
                <strong className="text-gray-900">Excellence:</strong> We strive for excellence in every endeavor, from research and development to community engagement and education.
              </li>
            </ul>
          </section>

          {/* Concerns */}
          <section className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 mb-6">Key Focus Areas</h2>
            <ul className="space-y-4 text-gray-700">
              <li>
                <strong className="text-gray-900">Climate Change:</strong> Addressing greenhouse gases, carbon emissions, and global temperature rise through innovative solutions and climate mitigation efforts.
              </li>
              <li>
                <strong className="text-gray-900">Environmental Impact:</strong> Reducing our carbon footprint, promoting recycling, and achieving carbon neutrality to ensure a healthy ecosystem.
              </li>
              <li>
                <strong className="text-gray-900">Digital Economy:</strong> Advancing AI, machine learning, robotics, and smart devices to drive the digital economy and the future of work.
              </li>
              <li>
                <strong className="text-gray-900">Digital Transformation:</strong> Enabling digital transformation through cloud computing, blockchain, augmented reality, and other emerging technologies.
              </li>
              <li>
                <strong className="text-gray-900">Data Science:</strong> Harnessing big data, predictive analytics, and cognitive computing to drive insights and innovation.
              </li>
              <li>
                <strong className="text-gray-900">AI and Innovation:</strong> Leveraging AI advancements, autonomous systems, and smart technology to improve various sectors, including healthcare, finance, education, and agriculture.
              </li>
            </ul>
          </section>

          {/* Closing Statement */}
          <section className="text-center mt-12">
            <p className="text-gray-700 italic">
              At CG4F, we are dedicated to creating greatness by transforming challenges into opportunities 
              and building a better, more sustainable world through technology and innovation.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
};

export default AboutUs;
