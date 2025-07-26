'use client';

import { useState, useMemo } from 'react';
import { Search, Filter } from 'lucide-react';
import BlogCard from '@/components/ui/BlogCard';
import type { BlogPost } from '@/types';
import type { Metadata } from 'next';

// Mock blog posts data (replace with actual data fetching)
const blogPosts: BlogPost[] = [
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
  },
  {
    slug: 'real-time-analytics-kafka',
    title: 'Real-time Analytics with Apache Kafka',
    excerpt: 'Explore how to build real-time analytics systems using Apache Kafka, Kafka Streams, and time-windowed aggregations.',
    date: '2023-12-28',
    readingTime: 10,
    category: 'Streaming',
    tags: ['Apache Kafka', 'Real-time', 'Streaming', 'Analytics'],
    published: true,
    content: ''
  },
  {
    slug: 'dbt-best-practices',
    title: 'dbt Best Practices for Data Transformation',
    excerpt: 'Essential patterns and practices for building maintainable and scalable data transformation workflows with dbt.',
    date: '2023-12-20',
    readingTime: 7,
    category: 'Tools',
    tags: ['dbt', 'Data Transformation', 'SQL', 'Best Practices'],
    published: true,
    content: ''
  },
  {
    slug: 'serverless-data-processing',
    title: 'Serverless Data Processing on AWS',
    excerpt: 'Cost-effective strategies for processing data using AWS Lambda, S3, and other serverless technologies.',
    date: '2023-12-15',
    readingTime: 9,
    category: 'Cloud Computing',
    tags: ['AWS', 'Serverless', 'Lambda', 'Cost Optimization'],
    published: true,
    content: ''
  },
  {
    slug: 'python-performance-optimization',
    title: 'Python Performance Optimization for Data Engineers',
    excerpt: 'Techniques to optimize Python code for data processing workloads, including profiling, vectorization, and parallel processing.',
    date: '2023-12-08',
    readingTime: 11,
    category: 'Programming',
    tags: ['Python', 'Performance', 'Optimization', 'Data Processing'],
    published: true,
    content: ''
  },
  {
    slug: 'data-engineering-career-guide',
    title: 'A Complete Guide to Starting Your Data Engineering Career',
    excerpt: 'Everything you need to know about breaking into data engineering, from essential skills to landing your first role.',
    date: '2023-11-30',
    readingTime: 15,
    category: 'Career',
    tags: ['Career', 'Data Engineering', 'Skills', 'Guide'],
    published: true,
    content: ''
  }
];

const categories = [
  'All',
  'Data Engineering',
  'Cloud Computing',
  'Best Practices',
  'Streaming',
  'Tools',
  'Programming',
  'Career',
];

export default function BlogPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const postsPerPage = 6;

  const filteredPosts = useMemo(() => {
    return blogPosts.filter(post => {
      const matchesSearch = searchTerm === '' || 
        post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.excerpt.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = selectedCategory === 'All' || post.category === selectedCategory;
      
      return matchesSearch && matchesCategory && post.published;
    });
  }, [searchTerm, selectedCategory]);

  const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
  const startIndex = (currentPage - 1) * postsPerPage;
  const currentPosts = filteredPosts.slice(startIndex, startIndex + postsPerPage);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen py-12">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
            Blog
          </h1>
          <p className="mt-4 text-lg leading-8 text-gray-600 dark:text-gray-300">
            Insights, tutorials, and thoughts on data engineering, cloud computing, and technology.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="mb-12 space-y-6">
          {/* Search Bar */}
          <div className="relative max-w-md mx-auto">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search articles..."
              value={searchTerm}
              onChange={handleSearch}
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg leading-5 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-green focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Categories:
              </span>
            </div>
            <div className="flex flex-wrap gap-2 justify-center">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => handleCategoryChange(category)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    selectedCategory === category
                      ? 'bg-primary-green text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results Summary */}
        <div className="mb-8 text-center">
          <p className="text-gray-600 dark:text-gray-300">
            {filteredPosts.length === 0 ? (
              'No articles found'
            ) : filteredPosts.length === 1 ? (
              '1 article found'
            ) : (
              `${filteredPosts.length} articles found`
            )}
            {searchTerm && (
              <span> for &quot;{searchTerm}&quot;</span>
            )}
            {selectedCategory !== 'All' && (
              <span> in {selectedCategory}</span>
            )}
          </p>
        </div>

        {/* Blog Posts Grid */}
        {currentPosts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {currentPosts.map((post) => (
              <BlogCard key={post.slug} post={post} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No articles found
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Try adjusting your search terms or browsing different categories.
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('All');
                setCurrentPage(1);
              }}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-green hover:bg-primary-green-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-green transition-colors"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 text-sm font-medium text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            
            {[...Array(totalPages)].map((_, index) => {
              const page = index + 1;
              return (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    currentPage === page
                      ? 'bg-primary-green text-white'
                      : 'text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  {page}
                </button>
              );
            })}
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 text-sm font-medium text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        )}

        {/* Newsletter Signup */}
        <div className="mt-16 bg-gradient-to-r from-primary-green/10 to-primary-blue/10 rounded-xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Stay Updated
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Get notified when I publish new articles about data engineering and cloud computing.
          </p>
          <form className="max-w-md mx-auto flex gap-4">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-primary-green text-white font-medium rounded-lg hover:bg-primary-green-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-green transition-colors"
            >
              Subscribe
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}