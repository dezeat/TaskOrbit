import Link from 'next/link';
import { Download, MapPin, Calendar, Award, Code, Database, Cloud, Wrench } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About',
  description: 'Learn more about my journey as a data engineer, my skills, and what drives my passion for data and technology.',
};

const skills = {
  programming: [
    { name: 'Python', level: 95 },
    { name: 'SQL', level: 90 },
    { name: 'Scala', level: 75 },
    { name: 'JavaScript/TypeScript', level: 80 },
    { name: 'Java', level: 70 },
  ],
  dataTools: [
    { name: 'Apache Spark', level: 85 },
    { name: 'Apache Airflow', level: 90 },
    { name: 'Apache Kafka', level: 80 },
    { name: 'dbt', level: 85 },
    { name: 'Pandas/NumPy', level: 95 },
  ],
  cloud: [
    { name: 'AWS (S3, EC2, Lambda)', level: 85 },
    { name: 'Google Cloud Platform', level: 80 },
    { name: 'Azure', level: 70 },
    { name: 'Docker/Kubernetes', level: 75 },
    { name: 'Terraform', level: 80 },
  ],
  databases: [
    { name: 'PostgreSQL', level: 90 },
    { name: 'Snowflake', level: 85 },
    { name: 'BigQuery', level: 80 },
    { name: 'Redis', level: 75 },
    { name: 'Elasticsearch', level: 70 },
  ],
};

const experiences = [
  {
    company: 'TechFlow Solutions',
    position: 'Senior Data Engineer',
    period: '2022 - Present',
    description: 'Leading the design and implementation of scalable data pipelines processing 50M+ records daily. Built real-time streaming architecture using Kafka and Spark.',
    achievements: [
      'Reduced data processing time by 60% through pipeline optimization',
      'Implemented automated data quality monitoring system',
      'Led migration to cloud-native architecture on AWS',
    ],
  },
  {
    company: 'DataVantage Corp',
    position: 'Data Engineer',
    period: '2021 - 2022',
    description: 'Developed ETL pipelines for financial analytics platform serving enterprise clients. Worked with large-scale data warehouse solutions.',
    achievements: [
      'Built automated reporting system serving 100+ clients',
      'Optimized database queries reducing execution time by 40%',
      'Implemented CI/CD for data pipeline deployments',
    ],
  },
  {
    company: 'Analytics Pro',
    position: 'Junior Data Engineer',
    period: '2020 - 2021',
    description: 'Started my data engineering journey working on customer analytics and reporting systems. Gained experience in Python, SQL, and cloud platforms.',
    achievements: [
      'Developed first production ETL pipeline',
      'Created data visualization dashboards',
      'Collaborated with data science team on ML feature engineering',
    ],
  },
];

function SkillBar({ name, level }: { name: string; level: number }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{name}</span>
      <div className="flex-1 mx-4">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-primary-green to-primary-blue h-2 rounded-full transition-all duration-1000 ease-out"
            style={{ width: `${level}%` }}
          />
        </div>
      </div>
      <span className="text-sm text-gray-500 dark:text-gray-400">{level}%</span>
    </div>
  );
}

function SkillCategory({ title, skills, icon }: { title: string; skills: Array<{ name: string; level: number }>; icon: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center mb-4">
        <div className="text-primary-green dark:text-primary-green-light mr-3">
          {icon}
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
      </div>
      {skills.map((skill) => (
        <SkillBar key={skill.name} name={skill.name} level={skill.level} />
      ))}
    </div>
  );
}

export default function AboutPage() {
  return (
    <div className="min-h-screen py-12">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
            About Me
          </h1>
          <p className="mt-4 text-lg leading-8 text-gray-600 dark:text-gray-300">
            Passionate about transforming data into actionable insights and building robust data infrastructure.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mb-16">
          {/* Personal Info */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700 text-center">
              <div className="w-32 h-32 mx-auto mb-6 bg-gradient-to-br from-primary-green to-primary-blue rounded-full flex items-center justify-center text-white text-4xl font-bold">
                DE
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Data Engineer
              </h2>
              <div className="space-y-2 text-gray-600 dark:text-gray-300 mb-6">
                <div className="flex items-center justify-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  <span>San Francisco, CA</span>
                </div>
                <div className="flex items-center justify-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  <span>3.5 years experience</span>
                </div>
                <div className="flex items-center justify-center">
                  <Award className="h-4 w-4 mr-2" />
                  <span>AWS Certified</span>
                </div>
              </div>
              <Link
                href="/resume.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-primary-green text-white px-6 py-3 rounded-lg hover:bg-primary-green-medium transition-colors"
              >
                <Download className="h-4 w-4" />
                Download Resume
              </Link>
            </div>
          </div>

          {/* Story */}
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">My Journey</h3>
              <div className="prose prose-lg dark:prose-invert max-w-none">
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  My passion for data engineering began during my computer science studies when I discovered 
                  the power of turning raw data into meaningful insights. What started as curiosity about 
                  databases and analytics quickly evolved into a career dedicated to building scalable data infrastructure.
                </p>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  Over the past 3.5 years, I&apos;ve had the privilege of working with diverse teams and technologies, 
                  from building real-time streaming pipelines that process millions of events daily to designing 
                  data warehouses that power critical business decisions.
                </p>
                <p className="text-gray-600 dark:text-gray-300">
                  When I&apos;m not engineering data solutions, you&apos;ll find me hiking in the beautiful California 
                  outdoors, contributing to open-source projects, or exploring the latest developments in cloud computing 
                  and machine learning. I believe in sustainable technology practices and enjoy mentoring aspiring 
                  data engineers.
                </p>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">What Drives Me</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-primary-green dark:text-primary-green-light mb-2">
                    🌱 Sustainable Tech
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Building efficient systems that minimize resource usage while maximizing impact.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-primary-green dark:text-primary-green-light mb-2">
                    🚀 Innovation
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Always exploring new technologies and methodologies to solve complex problems.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-primary-green dark:text-primary-green-light mb-2">
                    🤝 Collaboration
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Working with cross-functional teams to deliver data solutions that matter.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-primary-green dark:text-primary-green-light mb-2">
                    📚 Continuous Learning
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Staying current with industry trends and sharing knowledge with the community.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Skills Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
            Technical Skills
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <SkillCategory
              title="Programming"
              skills={skills.programming}
              icon={<Code className="h-6 w-6" />}
            />
            <SkillCategory
              title="Data Tools"
              skills={skills.dataTools}
              icon={<Wrench className="h-6 w-6" />}
            />
            <SkillCategory
              title="Cloud & DevOps"
              skills={skills.cloud}
              icon={<Cloud className="h-6 w-6" />}
            />
            <SkillCategory
              title="Databases"
              skills={skills.databases}
              icon={<Database className="h-6 w-6" />}
            />
          </div>
        </div>

        {/* Experience Timeline */}
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-12">
            Professional Experience
          </h2>
          <div className="space-y-8">
            {experiences.map((experience, index) => (
              <div
                key={index}
                className="relative bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700"
              >
                <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                      {experience.position}
                    </h3>
                    <p className="text-primary-green dark:text-primary-green-light font-semibold">
                      {experience.company}
                    </p>
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400 mt-1 md:mt-0">
                    {experience.period}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {experience.description}
                </p>
                <ul className="space-y-2">
                  {experience.achievements.map((achievement, achIndex) => (
                    <li
                      key={achIndex}
                      className="flex items-start text-sm text-gray-600 dark:text-gray-300"
                    >
                      <span className="text-primary-green dark:text-primary-green-light mr-2">•</span>
                      {achievement}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}