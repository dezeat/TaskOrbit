# Data Engineer Portfolio Website

A modern, minimalist portfolio website built for data engineers. Features a clean, nature-inspired design with green, blue, and white color palette, dark mode support, and comprehensive blog functionality.

![Portfolio Preview](https://via.placeholder.com/800x400/2D5A27/FFFFFF?text=Data+Engineer+Portfolio)

## ✨ Features

### 🎨 Design & UI
- **Modern Minimalist Design**: Clean, professional aesthetic with nature-inspired elements
- **Responsive Layout**: Mobile-first design that works on all devices
- **Dark/Light Mode**: Automatic theme detection with manual toggle
- **Smooth Animations**: Subtle transitions and hover effects
- **Accessibility**: WCAG 2.1 AA compliant with proper semantic HTML

### 📱 Pages & Functionality
- **Homepage**: Hero section with latest blog posts preview
- **About Page**: Professional background, skills visualization, and experience timeline
- **Projects Page**: Filterable project showcase with categories
- **Blog**: Full-featured blog with search, filtering, and pagination
- **Contact Page**: Contact form with social links and availability status
- **Individual Blog Posts**: Rich article pages with sharing and related posts

### 🚀 Technical Features
- **Static Site Generation**: Built with Next.js for optimal performance
- **TypeScript**: Full type safety throughout the application
- **Tailwind CSS**: Utility-first CSS framework for rapid development
- **SEO Optimized**: Proper meta tags, Open Graph, and Twitter Card support
- **GitHub Pages Ready**: Automated deployment with GitHub Actions
- **Performance Optimized**: Lighthouse score 90+ across all metrics

## 🛠️ Tech Stack

- **Framework**: [Next.js 14](https://nextjs.org/) with App Router
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Fonts**: [Inter](https://fonts.google.com/specimen/Inter) & [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono)
- **Deployment**: [GitHub Pages](https://pages.github.com/) via GitHub Actions
- **Package Manager**: npm

## 🚀 Quick Start

### Prerequisites
- Node.js 18.0 or later
- npm 8.0 or later

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/username/data-engineer-portfolio.git
   cd data-engineer-portfolio/portfolio-website
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
portfolio-website/
├── src/
│   ├── app/                 # App Router pages
│   │   ├── about/          # About page
│   │   ├── blog/           # Blog pages
│   │   ├── contact/        # Contact page
│   │   ├── projects/       # Projects page
│   │   ├── globals.css     # Global styles
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Homepage
│   ├── components/         # Reusable components
│   │   ├── ui/            # UI components
│   │   ├── Header.tsx     # Navigation header
│   │   ├── Footer.tsx     # Site footer
│   │   └── Layout.tsx     # Main layout wrapper
│   ├── content/           # Blog content (Markdown)
│   ├── lib/              # Utility functions
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
├── .github/              # GitHub Actions workflows
├── next.config.mjs       # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── package.json          # Dependencies and scripts
```

## 🎨 Customization

### Colors & Branding
The design system uses CSS custom properties defined in `tailwind.config.ts`:

```typescript
colors: {
  primary: {
    green: '#2D5A27',          // Dark forest green
    'green-medium': '#4A7C59',  // Medium green
    'green-light': '#A4C3A2',   // Light sage
    blue: '#1E3A8A',           // Deep blue
    'blue-light': '#3B82F6',    // Bright blue
  }
}
```

### Content Updates
1. **Personal Information**: Update contact details in `src/components/Footer.tsx` and `src/app/contact/page.tsx`
2. **About Page**: Modify experience and skills in `src/app/about/page.tsx`
3. **Projects**: Add your projects to the projects array in `src/app/projects/page.tsx`
4. **Blog Posts**: Add markdown files to `src/content/blog/` or update the mock data arrays

### Adding Blog Posts
Create new blog posts by adding objects to the `blogPosts` array in the relevant files:

```typescript
{
  slug: 'your-post-slug',
  title: 'Your Post Title',
  excerpt: 'Brief description of your post...',
  date: '2024-01-20',
  readingTime: 5,
  category: 'Data Engineering',
  tags: ['Tag1', 'Tag2'],
  published: true,
  content: 'Your blog post content in markdown...'
}
```

## 🚀 Deployment

### GitHub Pages (Recommended)

1. **Fork or clone this repository**
2. **Update the configuration**:
   - Modify `next.config.mjs` with your repository name
   - Update `package.json` homepage URL
3. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Set source to "GitHub Actions"
4. **Push to main branch** - deployment happens automatically!

### Alternative Deployment Options

- **Vercel**: Connect your GitHub repository at [vercel.com](https://vercel.com)
- **Netlify**: Deploy via [netlify.com](https://netlify.com) with build command `npm run build`
- **Custom Server**: Use `npm run build && npm start` for self-hosting

## 📊 Performance

This portfolio is optimized for performance:

- ⚡ **Lighthouse Score**: 90+ across all metrics
- 🚀 **First Contentful Paint**: < 2s
- 📱 **Mobile-friendly**: Responsive design with touch-friendly interactions
- 🔍 **SEO Optimized**: Proper meta tags and structured data
- ♿ **Accessible**: WCAG 2.1 AA compliant

## 🛠️ Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run export       # Build and export static files
npm run deploy       # Build with GitHub Pages optimization
npm run clean        # Clean build artifacts
npm run type-check   # Run TypeScript type checking
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- **Live Demo**: [Your Portfolio URL](https://username.github.io/portfolio-website)
- **Repository**: [GitHub](https://github.com/username/data-engineer-portfolio)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/username/data-engineer-portfolio/issues)

## 🙏 Acknowledgments

- Design inspiration from modern portfolio trends
- Icons by [Lucide](https://lucide.dev/)
- Fonts by [Google Fonts](https://fonts.google.com/)
- Built with [Next.js](https://nextjs.org/) and [Tailwind CSS](https://tailwindcss.com/)

---

**Made with 💚 for the data engineering community**

*Need help customizing this portfolio? Feel free to open an issue or reach out!*
