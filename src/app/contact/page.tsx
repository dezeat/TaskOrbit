'use client';

import { useState } from 'react';
import { Mail, MapPin, Phone, Github, Linkedin, Twitter, Send, CheckCircle } from 'lucide-react';
import type { Metadata } from 'next';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsSubmitting(false);
    setIsSubmitted(true);
    setFormData({ name: '', email: '', subject: '', message: '' });
    
    // Reset success state after 5 seconds
    setTimeout(() => setIsSubmitted(false), 5000);
  };

  const contactInfo = [
    {
      icon: Mail,
      label: 'Email',
      value: 'hello@dataengineer.dev',
      link: 'mailto:hello@dataengineer.dev',
    },
    {
      icon: MapPin,
      label: 'Location',
      value: 'San Francisco, CA',
      link: null,
    },
    {
      icon: Phone,
      label: 'Phone',
      value: '+1 (555) 123-4567',
      link: 'tel:+15551234567',
    },
  ];

  const socialLinks = [
    {
      icon: Github,
      label: 'GitHub',
      value: '@username',
      link: 'https://github.com/username',
      color: 'hover:text-gray-900 dark:hover:text-white',
    },
    {
      icon: Linkedin,
      label: 'LinkedIn',
      value: '/in/username',
      link: 'https://linkedin.com/in/username',
      color: 'hover:text-blue-600',
    },
    {
      icon: Twitter,
      label: 'Twitter',
      value: '@username',
      link: 'https://twitter.com/username',
      color: 'hover:text-blue-400',
    },
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
            Get in Touch
          </h1>
          <p className="mt-4 text-lg leading-8 text-gray-600 dark:text-gray-300">
            I&apos;d love to hear about your data challenges and explore how we can work together.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Information */}
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Let&apos;s Connect
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-8">
                Whether you have a project in mind, want to discuss data engineering best practices, 
                or just want to chat about the latest in cloud computing and analytics, I&apos;m always 
                happy to connect with fellow data enthusiasts.
              </p>
            </div>

            {/* Contact Details */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Contact Information
              </h3>
              {contactInfo.map((item, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-primary-green/10 rounded-lg flex items-center justify-center">
                      <item.icon className="h-5 w-5 text-primary-green dark:text-primary-green-light" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {item.label}
                    </p>
                    {item.link ? (
                      <a
                        href={item.link}
                        className="text-gray-600 dark:text-gray-300 hover:text-primary-green dark:hover:text-primary-green-light transition-colors"
                      >
                        {item.value}
                      </a>
                    ) : (
                      <p className="text-gray-600 dark:text-gray-300">
                        {item.value}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Social Links */}
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Social Media
              </h3>
              <div className="flex gap-4">
                {socialLinks.map((social, index) => (
                  <a
                    key={index}
                    href={social.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center text-gray-600 dark:text-gray-400 transition-colors ${social.color}`}
                    aria-label={social.label}
                  >
                    <social.icon className="h-5 w-5" />
                  </a>
                ))}
              </div>
            </div>

            {/* Availability */}
            <div className="bg-gradient-to-r from-primary-green/10 to-primary-blue/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Current Availability
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Available for freelance projects
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Open to consulting opportunities
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Always interested in tech discussions
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Form */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Send me a message
            </h2>

            {isSubmitted ? (
              <div className="text-center py-8">
                <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Message sent successfully!
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Thank you for reaching out. I&apos;ll get back to you within 24 hours.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      required
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="your.email@example.com"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="subject" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Subject *
                  </label>
                  <select
                    id="subject"
                    name="subject"
                    required
                    value={formData.subject}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Select a subject</option>
                    <option value="project">Project Collaboration</option>
                    <option value="consulting">Consulting Inquiry</option>
                    <option value="job">Job Opportunity</option>
                    <option value="question">Technical Question</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Message *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    value={formData.message}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                    placeholder="Tell me about your project, question, or how I can help..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-primary-green text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-green-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-green disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="h-5 w-5" />
                      Send Message
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-16 bg-gray-50 dark:bg-gray-800/50 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                What type of projects do you work on?
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                I specialize in data engineering projects including ETL/ELT pipelines, data warehousing, 
                real-time streaming, and cloud migration projects.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Do you offer consulting services?
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Yes! I provide consulting on data architecture, technology selection, 
                performance optimization, and team mentoring.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                What&apos;s your typical response time?
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                I aim to respond to all inquiries within 24 hours. For urgent matters, 
                feel free to mention it in your message.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Are you available for full-time roles?
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                I&apos;m currently focused on freelance and consulting work, but I&apos;m open to 
                discussing exceptional full-time opportunities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}