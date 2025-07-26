import Link from 'next/link';
import { Github, Linkedin, Mail, Twitter } from 'lucide-react';

const navigation = {
  main: [
    { name: 'About', href: '/about' },
    { name: 'Blog', href: '/blog' },
    { name: 'Projects', href: '/projects' },
    { name: 'Contact', href: '/contact' },
  ],
  social: [
    {
      name: 'GitHub',
      href: 'https://github.com',
      icon: Github,
    },
    {
      name: 'LinkedIn',
      href: 'https://linkedin.com',
      icon: Linkedin,
    },
    {
      name: 'Twitter',
      href: 'https://twitter.com',
      icon: Twitter,
    },
    {
      name: 'Email',
      href: 'mailto:hello@dataengineer.dev',
      icon: Mail,
    },
  ],
};

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="mx-auto max-w-7xl overflow-hidden px-6 py-12 sm:py-16 lg:px-8">
        <nav className="-mb-6 columns-2 sm:flex sm:justify-center sm:space-x-12" aria-label="Footer">
          {navigation.main.map((item) => (
            <div key={item.name} className="pb-6">
              <Link 
                href={item.href} 
                className="text-sm leading-6 text-gray-600 dark:text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
              >
                {item.name}
              </Link>
            </div>
          ))}
        </nav>
        
        <div className="mt-10 flex justify-center space-x-10">
          {navigation.social.map((item) => (
            <Link 
              key={item.name} 
              href={item.href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
            >
              <span className="sr-only">{item.name}</span>
              <item.icon className="h-6 w-6" aria-hidden="true" />
            </Link>
          ))}
        </div>
        
        <div className="mt-10 border-t border-gray-200 dark:border-gray-700 pt-8">
          <div className="text-center">
            <p className="text-xs leading-5 text-gray-500 dark:text-gray-400">
              &copy; {new Date().getFullYear()} Data Engineer Portfolio. Built with Next.js and Tailwind CSS.
            </p>
            <p className="mt-2 text-xs leading-5 text-gray-500 dark:text-gray-400">
              Designed with 🌱 for a sustainable digital future.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}