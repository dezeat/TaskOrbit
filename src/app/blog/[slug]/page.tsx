import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Calendar, Clock, ArrowLeft, Share2, Github, Linkedin, Twitter } from 'lucide-react';
import { formatDate } from '@/lib/utils';
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
    content: `
# Building Scalable ETL Pipelines with Apache Airflow

Data engineering is at the heart of modern analytics, and building reliable, scalable ETL (Extract, Transform, Load) pipelines is crucial for any data-driven organization. In this comprehensive guide, we'll explore how to design and implement robust ETL pipelines using Apache Airflow and Python.

## Why Apache Airflow?

Apache Airflow has become the de facto standard for workflow orchestration in the data engineering world. Here's why:

- **Workflow as Code**: Define your data pipelines as Python code
- **Rich UI**: Monitor and debug pipelines through a web interface
- **Extensible**: Vast ecosystem of operators and integrations
- **Scalable**: Built to handle complex, enterprise-scale workflows

## Pipeline Architecture

A well-designed ETL pipeline follows these principles:

1. **Modularity**: Break down complex processes into smaller, reusable tasks
2. **Idempotency**: Tasks should produce the same result when run multiple times
3. **Error Handling**: Graceful failure handling and retry mechanisms
4. **Monitoring**: Comprehensive logging and alerting

## Sample DAG Implementation

Here's a simple example of an ETL pipeline DAG:

\`\`\`python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

def extract_data(**context):
    # Extract data from source systems
    pass

def transform_data(**context):
    # Apply business logic and transformations
    pass

def load_data(**context):
    # Load data into target systems
    pass

dag = DAG(
    'customer_analytics_etl',
    default_args=default_args,
    description='Customer analytics ETL pipeline',
    schedule_interval='@daily',
    catchup=False
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag
)

extract_task >> transform_task >> load_task
\`\`\`

## Best Practices

### 1. Use Sensors for External Dependencies
When your pipeline depends on external systems, use sensors to wait for data availability:

\`\`\`python
from airflow.sensors.s3_key_sensor import S3KeySensor

wait_for_file = S3KeySensor(
    task_id='wait_for_source_file',
    bucket_name='data-lake',
    bucket_key='raw/{{ ds }}/customer_data.csv',
    timeout=3600,
    poke_interval=300,
    dag=dag
)
\`\`\`

### 2. Implement Data Quality Checks
Always validate your data at each stage:

\`\`\`python
def validate_data(**context):
    # Implement data quality checks
    assert row_count > 0, "No data found"
    assert null_percentage < 0.1, "Too many null values"
    return True

validation_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag
)
\`\`\`

### 3. Use XComs for Task Communication
Pass data between tasks using XComs:

\`\`\`python
def extract_and_count(**context):
    data = extract_data()
    context['task_instance'].xcom_push(key='record_count', value=len(data))
    return data

def process_data(**context):
    count = context['task_instance'].xcom_pull(key='record_count')
    print(f"Processing {count} records")
\`\`\`

## Monitoring and Alerting

Set up comprehensive monitoring:

- **Task-level alerts**: Email notifications on task failures
- **SLA monitoring**: Alert when tasks exceed expected runtime
- **Data freshness**: Monitor data pipeline latency
- **Custom metrics**: Track business-specific KPIs

## Scaling Considerations

As your data grows, consider these scaling strategies:

1. **Parallel Processing**: Use SubDAGs or TaskGroups for parallel execution
2. **Resource Allocation**: Configure appropriate resource pools
3. **Data Partitioning**: Process data in smaller, manageable chunks
4. **Caching**: Implement intelligent caching strategies

## Conclusion

Building scalable ETL pipelines with Apache Airflow requires careful planning, adherence to best practices, and continuous monitoring. By following the patterns outlined in this guide, you'll be well-equipped to handle enterprise-scale data processing challenges.

Remember: start simple, iterate quickly, and always prioritize data quality and reliability over complexity.

---

*Want to discuss ETL strategies or have questions about implementing Airflow in your organization? Feel free to reach out!*
    `
  },
  // Add other mock posts here if needed for related posts
];

interface BlogPostPageProps {
  params: {
    slug: string;
  };
}

export async function generateMetadata({ params }: BlogPostPageProps): Promise<Metadata> {
  const post = blogPosts.find(p => p.slug === params.slug);
  
  if (!post) {
    return {
      title: 'Post Not Found',
    };
  }

  return {
    title: post.title,
    description: post.excerpt,
    keywords: post.tags,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
    },
  };
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const post = blogPosts.find(p => p.slug === params.slug);
  
  if (!post) {
    notFound();
  }

  // Get related posts (excluding current post)
  const relatedPosts = blogPosts
    .filter(p => p.slug !== post.slug && p.published)
    .filter(p => p.category === post.category || p.tags.some(tag => post.tags.includes(tag)))
    .slice(0, 3);

  const shareUrl = typeof window !== 'undefined' ? window.location.href : '';
  const shareText = `Check out "${post.title}" - ${post.excerpt}`;

  return (
    <div className="min-h-screen py-12">
      <div className="mx-auto max-w-4xl px-6 lg:px-8">
        {/* Back Link */}
        <div className="mb-8">
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-primary-green dark:text-primary-green-light hover:text-primary-green-medium dark:hover:text-primary-green transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Blog
          </Link>
        </div>

        {/* Article Header */}
        <header className="mb-12">
          <div className="mb-4">
            <span className="inline-flex items-center rounded-full bg-primary-green-light/10 px-3 py-1 text-sm font-medium text-primary-green dark:text-primary-green-light">
              {post.category}
            </span>
          </div>
          
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl mb-6">
            {post.title}
          </h1>
          
          <div className="flex flex-wrap items-center gap-6 text-gray-600 dark:text-gray-400 mb-6">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <time dateTime={post.date}>{formatDate(post.date)}</time>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>{post.readingTime} min read</span>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2 mb-8">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-3 py-1 rounded-full text-sm"
              >
                #{tag.toLowerCase().replace(/\s+/g, '')}
              </span>
            ))}
          </div>

          {/* Share Buttons */}
          <div className="flex items-center gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Share:</span>
            <div className="flex gap-2">
              <a
                href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-gray-500 hover:text-blue-400 transition-colors"
                aria-label="Share on Twitter"
              >
                <Twitter className="h-5 w-5" />
              </a>
              <a
                href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-gray-500 hover:text-blue-600 transition-colors"
                aria-label="Share on LinkedIn"
              >
                <Linkedin className="h-5 w-5" />
              </a>
              <button
                onClick={() => navigator.clipboard.writeText(shareUrl)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                aria-label="Copy link"
              >
                <Share2 className="h-5 w-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Article Content */}
        <article className="prose prose-lg dark:prose-invert max-w-none mb-16">
          <div dangerouslySetInnerHTML={{ __html: post.content.replace(/\n/g, '<br />') }} />
        </article>

        {/* Author Bio */}
        <div className="bg-gradient-to-r from-primary-green/5 to-primary-blue/5 rounded-xl p-8 mb-16">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-shrink-0">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-green to-primary-blue rounded-full flex items-center justify-center text-white text-2xl font-bold">
                DE
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                About the Author
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                I'm a passionate data engineer with 3.5 years of experience building scalable data pipelines 
                and analytics solutions. I love sharing knowledge about data engineering best practices and 
                emerging technologies in the cloud computing space.
              </p>
              <div className="flex gap-4">
                <Link
                  href="/about"
                  className="text-primary-green dark:text-primary-green-light hover:underline"
                >
                  Learn more about me
                </Link>
                <Link
                  href="/contact"
                  className="text-primary-green dark:text-primary-green-light hover:underline"
                >
                  Get in touch
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Related Posts */}
        {relatedPosts.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              Related Articles
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {relatedPosts.map((relatedPost) => (
                <BlogCard key={relatedPost.slug} post={relatedPost} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}