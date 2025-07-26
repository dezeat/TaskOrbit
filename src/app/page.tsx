import Link from 'next/link';
import { ArrowRight, Download, Github, Linkedin, Mail } from 'lucide-react';
import BlogCard from '@/components/ui/BlogCard';
import type { BlogPost } from '@/types';

// Mock data for latest blog posts (replace with actual data fetching)
const latestPosts: BlogPost[] = [
  {
    slug: 'building-scalable-etl-pipelines',
    title: 'Building Scalable ETL Pipelines with Apache Airflow',
    excerpt: 'Learn how to design and implement robust ETL pipelines that can handle millions of records daily using Apache Airflow and Python.',
    date: '2024-01-15',
    readingTime: 8,
    category: 'Data Engineering',
    tags: ['Apache Airflow', 'ETL', 'Python', 'Data Pipeline'],
    published: true,
    content: ''
  },
  {
    slug: 'data-quality-monitoring',
    title: 'Implementing Data Quality Monitoring in Production',
    excerpt: 'Discover best practices for monitoring data quality in production environments and catch issues before they impact your analytics.',
    date: '2024-01-10',
    readingTime: 6,
    category: 'Best Practices',
    tags: ['Data Quality', 'Monitoring', 'Production', 'Analytics'],
    published: true,
    content: ''
  },
  {
    slug: 'cloud-data-warehousing',
    title: 'Choosing the Right Cloud Data Warehouse',
    excerpt: 'A comprehensive comparison of cloud data warehousing solutions including Snowflake, BigQuery, and Redshift.',
    date: '2024-01-05',
    readingTime: 12,
    category: 'Cloud Computing',
    tags: ['Snowflake', 'BigQuery', 'Redshift', 'Cloud'],
    published: true,
    content: ''
  }
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-green/5 via-primary-blue/5 to-primary-green-light/10 dark:from-primary-green/10 dark:via-primary-blue/10 dark:to-primary-green-light/20">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        
        <div className="relative mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-8">
              <span className="inline-flex items-center rounded-full bg-primary-green/10 px-4 py-2 text-sm font-medium text-primary-green dark:text-primary-green-light">
                👋 Welcome to my digital space
              </span>
            </div>
            
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
              Transforming Data into
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-green to-primary-blue">
                {' '}Insights
              </span>
            </h1>
            
            <p className="mt-6 text-lg leading-8 text-gray-600 dark:text-gray-300">
              I&apos;m a passionate data engineer with 3.5 years of experience building scalable data pipelines, 
              designing analytics solutions, and turning complex data challenges into business opportunities.
            </p>
            
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/projects"
                className="rounded-lg bg-primary-green px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-primary-green-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-green transition-all duration-200 flex items-center gap-2"
              >
                View My Work
                <ArrowRight className="h-4 w-4" />
              </Link>
              
              <Link
                href="/contact"
                className="rounded-lg border border-gray-300 dark:border-gray-600 px-6 py-3 text-sm font-semibold text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-800 transition-all duration-200"
              >
                Get in Touch
              </Link>
            </div>
            
            <div className="mt-8 flex items-center justify-center space-x-6">
              <Link 
                href="https://github.com" 
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
              >
                <Github className="h-6 w-6" />
                <span className="sr-only">GitHub</span>
              </Link>
              <Link 
                href="https://linkedin.com" 
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
              >
                <Linkedin className="h-6 w-6" />
                <span className="sr-only">LinkedIn</span>
              </Link>
              <Link 
                href="mailto:hello@dataengineer.dev"
                className="text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
              >
                <Mail className="h-6 w-6" />
                <span className="sr-only">Email</span>
              </Link>
            </div>
          </div>
        </div>
        
        {/* Floating elements for visual interest */}
        <div className="absolute top-1/4 left-10 w-20 h-20 bg-primary-green-light/20 rounded-full animate-float"></div>
        <div className="absolute top-3/4 right-10 w-32 h-32 bg-primary-blue/20 rounded-full animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-primary-green/20 rounded-full animate-float" style={{ animationDelay: '4s' }}></div>
      </section>

      {/* Latest Blog Posts */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Latest Insights
            </h2>
            <p className="mt-4 text-lg leading-8 text-gray-600 dark:text-gray-300">
              Sharing knowledge about data engineering, best practices, and industry trends.
            </p>
          </div>
          
          <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-x-8 gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
            {latestPosts.map((post) => (
              <BlogCard key={post.slug} post={post} />
            ))}
          </div>
          
          <div className="mt-16 text-center">
            <Link
              href="/blog"
              className="inline-flex items-center gap-2 text-primary-green dark:text-primary-green-light hover:text-primary-green-medium dark:hover:text-primary-green font-semibold transition-colors"
            >
              View all posts
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-green dark:bg-primary-green-medium">
        <div className="px-6 py-24 sm:px-6 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to collaborate?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-green-100">
              I&apos;m always excited to work on interesting data challenges and connect with fellow engineers and data enthusiasts.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/contact"
                className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-primary-green shadow-sm hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
              >
                Start a Conversation
              </Link>
              <Link
                href="/resume.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-white/20 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10 transition-all duration-200 flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Download Resume
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}