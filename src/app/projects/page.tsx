'use client';

import { useState } from 'react';
import { Filter } from 'lucide-react';
import ProjectCard from '@/components/ui/ProjectCard';
import type { Project } from '@/types';
import type { Metadata } from 'next';

// Mock projects data (replace with actual data fetching)
const projects: Project[] = [
  {
    id: '1',
    title: 'Real-time Data Pipeline with Kafka & Spark',
    description: 'Built a scalable real-time data pipeline processing 1M+ events per hour using Apache Kafka, Spark Streaming, and Elasticsearch. Implemented automated data quality checks and monitoring.',
    image: '/projects/pipeline.jpg',
    technologies: ['Apache Kafka', 'Apache Spark', 'Elasticsearch', 'Python', 'Docker', 'AWS'],
    githubUrl: 'https://github.com/username/kafka-spark-pipeline',
    category: 'data-engineering',
    featured: true,
  },
  {
    id: '2',
    title: 'Customer Analytics Data Warehouse',
    description: 'Designed and implemented a cloud-native data warehouse on Snowflake for customer analytics. Built ETL pipelines with dbt and automated reporting dashboard.',
    image: '/projects/warehouse.jpg',
    technologies: ['Snowflake', 'dbt', 'Apache Airflow', 'Tableau', 'SQL', 'Python'],
    githubUrl: 'https://github.com/username/customer-analytics-dw',
    liveUrl: 'https://demo.customeranalytics.com',
    category: 'data-engineering',
    featured: true,
  },
  {
    id: '3',
    title: 'ML Feature Store with MLflow',
    description: 'Developed a centralized feature store for machine learning workflows using MLflow, Redis, and FastAPI. Enables feature sharing across ML teams.',
    image: '/projects/feature-store.jpg',
    technologies: ['MLflow', 'FastAPI', 'Redis', 'PostgreSQL', 'Python', 'Docker'],
    githubUrl: 'https://github.com/username/ml-feature-store',
    category: 'data-science',
    featured: false,
  },
  {
    id: '4',
    title: 'Open Source Data Quality Library',
    description: 'Created an open-source Python library for data quality validation and monitoring. Supports pandas, Spark, and SQL databases with extensible rules engine.',
    image: '/projects/data-quality.jpg',
    technologies: ['Python', 'Pandas', 'PySpark', 'SQLAlchemy', 'pytest', 'GitHub Actions'],
    githubUrl: 'https://github.com/username/data-quality-lib',
    liveUrl: 'https://pypi.org/project/data-quality-lib/',
    category: 'open-source',
    featured: false,
  },
  {
    id: '5',
    title: 'Serverless ETL with AWS Lambda',
    description: 'Built cost-effective serverless ETL pipelines using AWS Lambda, S3, and EventBridge. Processes CSV and JSON files with automatic schema detection.',
    image: '/projects/serverless-etl.jpg',
    technologies: ['AWS Lambda', 'AWS S3', 'AWS EventBridge', 'Python', 'Terraform', 'CloudFormation'],
    githubUrl: 'https://github.com/username/serverless-etl',
    category: 'data-engineering',
    featured: false,
  },
  {
    id: '6',
    title: 'Portfolio Website',
    description: 'This modern, responsive portfolio website built with Next.js, TypeScript, and Tailwind CSS. Features dark mode, blog functionality, and static site generation.',
    image: '/projects/portfolio.jpg',
    technologies: ['Next.js', 'TypeScript', 'Tailwind CSS', 'Vercel', 'MDX'],
    githubUrl: 'https://github.com/username/portfolio-website',
    liveUrl: 'https://your-portfolio.com',
    category: 'web-development',
    featured: false,
  },
];

const categories = [
  { value: 'all', label: 'All Projects' },
  { value: 'data-engineering', label: 'Data Engineering' },
  { value: 'data-science', label: 'Data Science' },
  { value: 'web-development', label: 'Web Development' },
  { value: 'open-source', label: 'Open Source' },
];

export default function ProjectsPage() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  const filteredProjects = selectedCategory === 'all' 
    ? projects 
    : projects.filter(project => project.category === selectedCategory);

  const featuredProjects = filteredProjects.filter(project => project.featured);
  const otherProjects = filteredProjects.filter(project => !project.featured);

  return (
    <div className="min-h-screen py-12">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
            My Projects
          </h1>
          <p className="mt-4 text-lg leading-8 text-gray-600 dark:text-gray-300">
            A showcase of data engineering solutions, open-source contributions, and technical experiments.
          </p>
        </div>

        {/* Filters */}
        <div className="mb-12">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Filter by category:
              </span>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.value}
                  onClick={() => setSelectedCategory(category.value)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    selectedCategory === category.value
                      ? 'bg-primary-green text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {category.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Featured Projects */}
        {featuredProjects.length > 0 && (
          <section className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              Featured Projects
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {featuredProjects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </section>
        )}

        {/* Other Projects */}
        {otherProjects.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              {featuredProjects.length > 0 ? 'Other Projects' : 'All Projects'}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {otherProjects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </section>
        )}

        {/* No Projects Found */}
        {filteredProjects.length === 0 && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No projects found
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Try selecting a different category or check back later for new projects.
            </p>
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-primary-green/10 to-primary-blue/10 rounded-xl p-8">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Have a project in mind?
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              I&apos;m always interested in collaborating on exciting data engineering challenges.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/contact"
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-green hover:bg-primary-green-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-green transition-colors"
              >
                Get in Touch
              </a>
              <a
                href="https://github.com/username"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 dark:border-gray-600 text-base font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-green transition-colors"
              >
                View GitHub
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}