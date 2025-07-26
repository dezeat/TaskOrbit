export interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  readingTime: number;
  category: string;
  tags: string[];
  published: boolean;
  content: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  technologies: string[];
  githubUrl?: string;
  liveUrl?: string;
  category: 'data-engineering' | 'web-development' | 'data-science' | 'open-source';
  featured: boolean;
}

export interface Experience {
  company: string;
  position: string;
  startDate: string;
  endDate?: string;
  description: string;
  technologies: string[];
}

export interface Skill {
  name: string;
  category: 'programming' | 'data-tools' | 'cloud' | 'frameworks' | 'databases';
  proficiency: 'beginner' | 'intermediate' | 'advanced' | 'expert';
}