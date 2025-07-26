import Link from 'next/link';
import { Calendar, Clock } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import type { BlogPost } from '@/types';

interface BlogCardProps {
  post: BlogPost;
}

export default function BlogCard({ post }: BlogCardProps) {
  return (
    <article className="group relative bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-primary-green-light dark:hover:border-primary-green-light transition-all duration-300">
      <div className="p-6">
        <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <time dateTime={post.date}>{formatDate(post.date)}</time>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{post.readingTime} min read</span>
          </div>
        </div>
        
        <div className="mb-3">
          <span className="inline-flex items-center rounded-full bg-primary-green-light/10 px-2.5 py-0.5 text-xs font-medium text-primary-green dark:text-primary-green-light">
            {post.category}
          </span>
        </div>
        
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-green dark:group-hover:text-primary-green-light transition-colors">
          <Link href={`/blog/${post.slug}`} className="stretched-link">
            {post.title}
          </Link>
        </h3>
        
        <p className="text-gray-600 dark:text-gray-300 line-clamp-3 mb-4">
          {post.excerpt}
        </p>
        
        <div className="flex flex-wrap gap-2">
          {post.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded-md"
            >
              {tag}
            </span>
          ))}
          {post.tags.length > 3 && (
            <span className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400">
              +{post.tags.length - 3} more
            </span>
          )}
        </div>
      </div>
      
      <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-primary-green to-primary-blue transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 rounded-b-xl" />
    </article>
  );
}