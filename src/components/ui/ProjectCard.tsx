import Link from 'next/link';
import Image from 'next/image';
import { Github, ExternalLink, Calendar } from 'lucide-react';
import type { Project } from '@/types';

interface ProjectCardProps {
  project: Project;
}

export default function ProjectCard({ project }: ProjectCardProps) {
  return (
    <article className="group relative bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-primary-green-light dark:hover:border-primary-green-light transition-all duration-300 overflow-hidden">
      {/* Project Image */}
      <div className="relative h-48 bg-gradient-to-br from-primary-green/10 to-primary-blue/10 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-4xl text-primary-green dark:text-primary-green-light opacity-20">
            📊
          </div>
        </div>
        {project.featured && (
          <div className="absolute top-4 left-4">
            <span className="bg-primary-green text-white text-xs font-medium px-2.5 py-1 rounded-full">
              Featured
            </span>
          </div>
        )}
      </div>

      <div className="p-6">
        {/* Category Badge */}
        <div className="mb-3">
          <span className="inline-flex items-center rounded-full bg-primary-green-light/10 px-2.5 py-0.5 text-xs font-medium text-primary-green dark:text-primary-green-light capitalize">
            {project.category.replace('-', ' ')}
          </span>
        </div>

        {/* Project Title */}
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-green dark:group-hover:text-primary-green-light transition-colors">
          {project.title}
        </h3>

        {/* Project Description */}
        <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
          {project.description}
        </p>

        {/* Technologies */}
        <div className="flex flex-wrap gap-2 mb-4">
          {project.technologies.slice(0, 4).map((tech) => (
            <span
              key={tech}
              className="inline-flex items-center text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded-md"
            >
              {tech}
            </span>
          ))}
          {project.technologies.length > 4 && (
            <span className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400">
              +{project.technologies.length - 4} more
            </span>
          )}
        </div>

        {/* Action Links */}
        <div className="flex items-center gap-4">
          {project.githubUrl && (
            <Link
              href={project.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
            >
              <Github className="h-4 w-4" />
              Code
            </Link>
          )}
          {project.liveUrl && (
            <Link
              href={project.liveUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
            >
              <ExternalLink className="h-4 w-4" />
              Live Demo
            </Link>
          )}
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-primary-green to-primary-blue transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
    </article>
  );
}