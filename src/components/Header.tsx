'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Menu, X, Moon, Sun } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HeaderProps {
  isDark: boolean;
  toggleTheme: () => void;
}

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'About', href: '/about' },
  { name: 'Blog', href: '/blog' },
  { name: 'Projects', href: '/projects' },
  { name: 'Contact', href: '/contact' },
];

export default function Header({ isDark, toggleTheme }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5">
            <span className="text-2xl font-bold text-primary-green dark:text-primary-green-light">
              DE
            </span>
          </Link>
        </div>
        
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700 dark:text-gray-300"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        
        <div className="hidden lg:flex lg:gap-x-12">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="text-sm font-semibold leading-6 text-gray-900 dark:text-gray-100 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
            >
              {item.name}
            </Link>
          ))}
        </div>
        
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-4">
          <button
            onClick={toggleTheme}
            className="rounded-md p-2 text-gray-700 dark:text-gray-300 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
            aria-label="Toggle theme"
          >
            {isDark ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </button>
          
          <Link
            href="/resume.pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md bg-primary-green px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-green-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-green transition-colors"
          >
            Resume
          </Link>
        </div>
      </nav>
      
      {/* Mobile menu */}
      <div className={cn(
        "fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white dark:bg-gray-900 px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10 transition-transform duration-300",
        mobileMenuOpen ? "translate-x-0" : "translate-x-full"
      )}>
        <div className="flex items-center justify-between">
          <Link href="/" className="-m-1.5 p-1.5" onClick={() => setMobileMenuOpen(false)}>
            <span className="text-2xl font-bold text-primary-green dark:text-primary-green-light">
              DE
            </span>
          </Link>
          <button
            type="button"
            className="-m-2.5 rounded-md p-2.5 text-gray-700 dark:text-gray-300"
            onClick={() => setMobileMenuOpen(false)}
          >
            <span className="sr-only">Close menu</span>
            <X className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        
        <div className="mt-6 flow-root">
          <div className="-my-6 divide-y divide-gray-500/10">
            <div className="space-y-2 py-6">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </div>
            
            <div className="py-6 space-y-2">
              <button
                onClick={toggleTheme}
                className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 w-full text-left"
              >
                {isDark ? 'Light Mode' : 'Dark Mode'}
              </button>
              
              <Link
                href="/resume.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="-mx-3 block rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-white bg-primary-green hover:bg-primary-green-medium text-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Resume
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Backdrop */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm lg:hidden" 
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </header>
  );
}