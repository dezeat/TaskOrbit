# Portfolio Website Setup Guide

This guide will help you customize this data engineer portfolio website to showcase your unique experience and projects.

## 🎯 Quick Customization Checklist

### 1. Personal Information (Required)
- [ ] Update your name and title in `src/app/layout.tsx` (metadata)
- [ ] Replace contact email in `src/components/Footer.tsx` and `src/app/contact/page.tsx`
- [ ] Update location in `src/app/about/page.tsx` and `src/app/contact/page.tsx`
- [ ] Add your social media links in both Footer and Contact pages
- [ ] Replace placeholder resume with your actual PDF in `public/resume.pdf`

### 2. About Page Content
Edit `src/app/about/page.tsx`:
- [ ] Update personal story and journey section
- [ ] Modify skills levels and categories to match your expertise
- [ ] Replace work experience with your actual job history
- [ ] Update years of experience (currently set to 3.5 years)
- [ ] Change location from San Francisco to your actual location

### 3. Projects Showcase
Edit `src/app/projects/page.tsx`:
- [ ] Replace sample projects with your actual work
- [ ] Add project screenshots to `public/projects/`
- [ ] Update GitHub and live demo URLs
- [ ] Adjust project categories to match your work

### 4. Blog Content
- [ ] Update blog posts in `src/app/page.tsx` and `src/app/blog/page.tsx`
- [ ] Create actual blog post content in `src/app/blog/[slug]/page.tsx`
- [ ] Add your own articles or remove blog functionality if not needed

### 5. Branding & Colors
If you want to change the color scheme:
- [ ] Update colors in `tailwind.config.ts`
- [ ] Consider changing the green/blue theme to match your preference

## 📝 Content Customization Templates

### Personal Bio Template
Replace the content in the About page with something like:

```markdown
My passion for data engineering began [when/where you started]. 
I specialize in [your specialties] and have experience with [key technologies].

Over the past [X] years, I've worked on [types of projects] and have 
helped organizations [achievements/impact].

When I'm not building data pipelines, I enjoy [personal interests].
```

### Project Description Template
```typescript
{
  id: 'project-id',
  title: 'Your Project Name',
  description: 'Brief 2-3 sentence description focusing on the problem solved and technologies used.',
  image: '/projects/your-project-image.jpg',
  technologies: ['Tech1', 'Tech2', 'Tech3'],
  githubUrl: 'https://github.com/yourusername/project',
  liveUrl: 'https://your-demo-url.com', // Optional
  category: 'data-engineering', // or 'data-science', 'web-development', 'open-source'
  featured: true // Set to true for your best projects
}
```

## 🚀 Deployment Steps

### GitHub Pages Setup
1. **Create a new repository** on GitHub (can be named anything)
2. **Upload your code** to the repository
3. **Update configuration**:
   - In `next.config.mjs`: Change `basePath` and `assetPrefix` to match your repo name
   - In `package.json`: Update the `homepage` field with your GitHub Pages URL
4. **Enable GitHub Pages**:
   - Go to Settings → Pages in your repository
   - Set Source to "GitHub Actions"
5. **Push to main branch** - automatic deployment will start!

### Configuration Updates Needed
In `next.config.mjs`, replace `'/portfolio-website'` with your actual repository name:
```javascript
basePath: process.env.NODE_ENV === 'production' ? '/your-repo-name' : '',
assetPrefix: process.env.NODE_ENV === 'production' ? '/your-repo-name/' : '',
```

## 🎨 Design Customization

### Changing Colors
Edit `tailwind.config.ts` to update the color scheme:
```typescript
colors: {
  primary: {
    green: '#YOUR_COLOR',        // Main brand color
    'green-medium': '#YOUR_COLOR', // Medium shade
    'green-light': '#YOUR_COLOR',  // Light shade
    blue: '#YOUR_COLOR',         // Accent color
    'blue-light': '#YOUR_COLOR', // Light accent
  }
}
```

### Adding Your Photo
1. Add your professional photo to `public/images/profile.jpg`
2. Update the About page to use the image instead of the placeholder initials

### Custom Fonts
To use different fonts, update `src/app/layout.tsx`:
```typescript
import { YourFont } from "next/font/google";

const yourFont = YourFont({ 
  subsets: ["latin"],
  variable: "--font-your-font",
});
```

## 📊 Content Strategy

### Blog Topics (if including blog)
Consider writing about:
- **Technical Tutorials**: ETL best practices, tool comparisons
- **Project Deep Dives**: Detailed case studies of your work
- **Industry Insights**: Trends in data engineering, cloud computing
- **Career Advice**: Tips for breaking into data engineering
- **Tool Reviews**: Honest reviews of data tools you've used

### Project Selection Tips
Choose projects that show:
- **Scalability**: Projects handling large data volumes
- **Real Impact**: Solutions that solved actual business problems
- **Technical Depth**: Complex engineering challenges overcome
- **Diverse Skills**: Different tools, languages, and platforms

## 🔧 Advanced Customization

### Adding New Pages
1. Create a new folder in `src/app/`
2. Add a `page.tsx` file with your content
3. Update navigation in `src/components/Header.tsx`

### Custom Components
Add reusable components to `src/components/ui/` and import them where needed.

### Analytics Setup
To add Google Analytics:
1. Get your GA tracking ID
2. Add the script to `src/app/layout.tsx`
3. Implement page view tracking

## 🐛 Troubleshooting

### Build Errors
- Ensure all images referenced in code exist in the `public` folder
- Check that all TypeScript types are correct
- Verify all imports are valid

### Deployment Issues
- Make sure your repository name matches the `basePath` in `next.config.mjs`
- Check that GitHub Actions are enabled in your repository settings
- Verify that the GitHub Pages source is set to "GitHub Actions"

### Styling Issues
- Run `npm run dev` to see changes in real-time
- Check browser developer tools for CSS conflicts
- Ensure Tailwind classes are spelled correctly

## 📞 Getting Help

- **Documentation**: Check the main README.md for detailed information
- **Issues**: Open an issue on the GitHub repository
- **Community**: Join data engineering communities for advice

Remember: Start with the basics (personal info, contact details) and gradually customize the design and content to match your unique style and experience!