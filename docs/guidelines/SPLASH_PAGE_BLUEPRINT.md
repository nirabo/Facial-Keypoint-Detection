# Complete Blueprint: Building a Modern Marketing Splash Page

## Project Overview

This blueprint provides step-by-step instructions for creating a professional, production-ready marketing landing page using React, TypeScript, Vite, and TailwindCSS. The resulting application will be:

- **Modern**: Built with latest web technologies and best practices
- **Performant**: Optimized builds, fast loading, smooth animations
- **Maintainable**: Data-driven architecture with clear separation of concerns
- **Internationalized**: Multi-language support out of the box
- **Production-ready**: Includes linting, formatting, git hooks, and deployment config

---

## Phase 1: Project Initialization

### 1.1 Create Vite + React + TypeScript Project

```bash
npm create vite@latest your-project-name -- --template react-ts
cd your-project-name
npm install
```

### 1.2 Install Core Dependencies

```bash
# UI Framework
npm install lucide-react

# Internationalization
npm install i18next react-i18next i18next-browser-languagedetector

# Styling
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 1.3 Install Development Dependencies

```bash
# Code Quality
npm install -D eslint @eslint/js typescript-eslint
npm install -D eslint-plugin-react-hooks eslint-plugin-react-refresh
npm install -D prettier

# Git Hooks
npm install -D husky lint-staged
```

### 1.4 Initialize Git and Husky

```bash
git init
npm run prepare
npx husky init
```

---

## Phase 2: Configuration Files

### 2.1 TypeScript Configuration

Create or update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}
```

Create `tsconfig.app.json` for application code and `tsconfig.node.json` for Vite config.

### 2.2 Vite Configuration

Create `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    host: '0.0.0.0',
  },
});
```

### 2.3 TailwindCSS Configuration

Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

### 2.4 Prettier Configuration

Create `.prettierrc`:

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### 2.5 ESLint Configuration

Create `eslint.config.js`:

```javascript
import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  }
);
```

### 2.6 Git Hooks Configuration

Create `.husky/pre-commit`:

```bash
npx lint-staged
```

Update `package.json` with lint-staged configuration:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview",
    "format": "prettier --write .",
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{html,css,md,json}": [
      "prettier --write"
    ]
  }
}
```

### 2.7 Git Ignore

Create `.gitignore`:

```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
```

---

## Phase 3: Base Styles and Setup

### 3.1 Main CSS File

Create `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 3.2 Custom Animations

Create `src/App.css`:

```css
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.8s ease-out forwards;
}

.animate-fadeSlideUp {
  animation: fadeSlideUp 0.8s ease-out forwards;
}

html {
  scroll-behavior: smooth;
}

@media (prefers-reduced-motion) {
  html {
    scroll-behavior: auto;
  }

  .animate-fadeIn,
  .animate-fadeSlideUp {
    animation: none;
  }
}
```

---

## Phase 4: Type Definitions

### 4.1 Create Type Interfaces

Create `src/types/index.ts`:

```typescript
export interface Testimonial {
  id: number;
  name: string;
  role: string;
  company: string;
  content: string;
  imageUrl: string;
}

export interface PricingPlan {
  id: number;
  name: string;
  price: string;
  description: string;
  features: string[];
  highlighted?: boolean;
}

export interface FeatureCard {
  id: number;
  title: string;
  description: string;
  icon: string;
}

export interface UseCaseCard {
  id: number;
  title: string;
  description: string;
  imageUrl: string;
  industry: string;
}
```

---

## Phase 5: Data Layer

Create static content files in `src/data/` directory. This separates content from UI logic.

### 5.1 Features Data

Create `src/data/features.ts`:

```typescript
import { FeatureCard } from '../types';

export const features: FeatureCard[] = [
  {
    id: 1,
    title: 'Feature One',
    description: 'Description of your first key feature',
    icon: 'WandSparklesIcon',
  },
  {
    id: 2,
    title: 'Feature Two',
    description: 'Description of your second key feature',
    icon: 'BrainIcon',
  },
  // Add 6-8 features total
];
```

### 5.2 Use Cases Data

Create `src/data/useCases.ts`:

```typescript
import { UseCaseCard } from '../types';

export const useCases: UseCaseCard[] = [
  {
    id: 1,
    title: 'Industry Use Case 1',
    description: 'How your product helps this industry',
    imageUrl: 'https://images.unsplash.com/photo-...',
    industry: 'Retail',
  },
  // Add 4-6 use cases
];
```

### 5.3 Testimonials Data

Create `src/data/testimonials.ts`:

```typescript
import { Testimonial } from '../types';

export const testimonials: Testimonial[] = [
  {
    id: 1,
    name: 'John Doe',
    role: 'CEO',
    company: 'Company Name',
    content: 'This product transformed our business...',
    imageUrl: 'https://i.pravatar.cc/150?img=1',
  },
  // Add 3-4 testimonials
];
```

### 5.4 Pricing Data

Create `src/data/pricingPlans.ts`:

```typescript
import { PricingPlan } from '../types';

export const pricingPlans: PricingPlan[] = [
  {
    id: 1,
    name: 'Starter',
    price: '$29',
    description: 'Perfect for small teams',
    features: [
      'Feature 1',
      'Feature 2',
      'Feature 3',
    ],
    highlighted: false,
  },
  {
    id: 2,
    name: 'Professional',
    price: '$99',
    description: 'For growing businesses',
    features: [
      'Everything in Starter',
      'Advanced Feature 1',
      'Advanced Feature 2',
    ],
    highlighted: true,
  },
  // Add 3 pricing tiers
];
```

---

## Phase 6: Internationalization Setup

### 6.1 Create i18n Configuration

Create `src/i18n/index.ts`:

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import bg from './locales/bg.json';

const resources = {
  en: {
    translation: en,
  },
  bg: {
    translation: bg,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  });

export default i18n;
```

### 6.2 Create Translation Files

Create `src/i18n/locales/en.json`:

```json
{
  "common": {
    "brandName": "YourBrand",
    "login": "Login",
    "tryDashboard": "Try Dashboard",
    "features": "Features",
    "useCases": "Use Cases",
    "solutions": "Solutions",
    "pricing": "Pricing"
  },
  "hero": {
    "title": "Transform Your Business",
    "subtitle": "Powerful solution for modern teams",
    "cta": "Get Started Free"
  },
  "features": {
    "sectionTitle": "Features",
    "mainTitle": "Everything You Need",
    "mainDescription": "Comprehensive tools to power your workflow"
  }
}
```

Create `src/i18n/locales/bg.json` with Bulgarian translations.

### 6.3 Initialize i18n in Main App

Update `src/main.tsx`:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import './i18n';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## Phase 7: Shared Components

### 7.1 Create Reusable Button Component

Create `src/components/Button.tsx`:

```typescript
import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  onClick,
  type = 'button',
  disabled = false,
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium transition-colors duration-200 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variantStyles = {
    primary: 'bg-blue-900 text-white hover:bg-blue-800 focus:ring-blue-700',
    secondary: 'bg-teal-600 text-white hover:bg-teal-700 focus:ring-teal-500',
    outline: 'border border-blue-900 text-blue-900 hover:bg-blue-50 focus:ring-blue-700',
    text: 'text-blue-900 hover:bg-blue-50 focus:ring-blue-700',
  };

  const sizeStyles = {
    sm: 'text-sm px-3 py-1.5',
    md: 'text-base px-4 py-2',
    lg: 'text-lg px-6 py-3',
  };

  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <button
      type={type}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${disabledStyles} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;
```

---

## Phase 8: Section Components

Create each section component in `src/components/`. Each section follows a similar pattern:

1. Import necessary dependencies (React, icons, data, translations)
2. Define component with TypeScript
3. Use hooks (useState, useEffect, useTranslation)
4. Return JSX with Tailwind styling

### 8.1 Navbar Component

Create `src/components/Navbar.tsx`:

**Key Features:**

- Fixed positioning with scroll detection
- Mobile hamburger menu
- Language selector dropdown
- Smooth transitions
- Accessibility (aria-labels)

**Implementation Pattern:**

```typescript
import React, { useState, useEffect } from 'react';
import { Menu, X, ChevronDown, Eye, Globe } from 'lucide-react';
import Button from './Button';
import { useTranslation } from 'react-i18next';

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
  const { t, i18n } = useTranslation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Render desktop nav, mobile nav, language selector
  // Use conditional classes based on scroll state
  // Include dropdown menus for Solutions
};
```

### 8.2 Hero Section

Create `src/components/HeroSection.tsx`:

**Key Features:**

- Large hero image or gradient background
- Main headline and subheadline
- Primary CTA buttons
- Fade-in animations

### 8.3 Feature Section

Create `src/components/FeatureSection.tsx`:

**Key Pattern: Icon Resolution**

```typescript
import {
  Wand2 as WandSparklesIcon,
  Brain as BrainIcon,
  // Import all icons used in features
} from 'lucide-react';

const iconComponents: Record<string, React.FC<{ className?: string }>> = {
  WandSparklesIcon,
  BrainIcon,
  // Map all icon names
};

// In render:
features.map(feature => {
  const IconComponent = iconComponents[feature.icon];
  return (
    <div key={feature.id}>
      {IconComponent && <IconComponent className="w-6 h-6" />}
      <h3>{t(`features.items.${featureId}.title`)}</h3>
    </div>
  );
});
```

### 8.4 How It Works Section (Optional)

Create `src/components/HowItWorksSection.tsx`:

**Features:**

- Step-by-step process visualization
- Numbered cards or timeline
- Illustrations or icons for each step

### 8.5 Use Cases Section

Create `src/components/UseCasesSection.tsx`:

**Key Features:**

- Filterable tabs by industry
- Image cards with hover effects
- Category switching with state management

**Pattern:**

```typescript
const [activeIndustry, setActiveIndustry] = useState('All');

const filteredCases = useCases.filter(
  uc => activeIndustry === 'All' || uc.industry === activeIndustry
);

// Render industry tabs
// Render filtered cards
```

### 8.6 Testimonials Section

Create `src/components/TestimonialsSection.tsx`:

**Features:**

- Customer quotes with photos
- Company names and roles
- Grid or carousel layout
- Avatar images

### 8.7 Pricing Section

Create `src/components/PricingSection.tsx`:

**Key Features:**

- Monthly/Annual toggle
- Highlighted "popular" plan
- Feature lists with checkmarks
- CTA buttons for each tier

**Pattern:**

```typescript
const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

// Calculate price based on billing cycle
// Highlight recommended plan with different styling
```

### 8.8 Demo Request Section

Create `src/components/DemoSection.tsx`:

**Features:**

- Form with controlled inputs
- Validation
- Submit state management
- Success/error messages

**Pattern:**

```typescript
const [formData, setFormData] = useState({
  name: '',
  email: '',
  company: '',
  message: '',
});
const [isSubmitting, setIsSubmitting] = useState(false);

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // Handle form submission
};
```

### 8.9 CTA Section

Create `src/components/CTASection.tsx`:

**Features:**

- Final call-to-action
- Compelling headline
- Large button
- Gradient or colored background

### 8.10 Footer

Create `src/components/Footer.tsx`:

**Features:**

- Company links (About, Blog, Careers)
- Product links
- Social media icons
- Copyright notice
- Multi-column layout

---

## Phase 9: Main App Component

### 9.1 Compose All Sections

Update `src/App.tsx`:

```typescript
import React from 'react';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import FeatureSection from './components/FeatureSection';
import HowItWorksSection from './components/HowItWorksSection';
import UseCasesSection from './components/UseCasesSection';
import TestimonialsSection from './components/TestimonialsSection';
import PricingSection from './components/PricingSection';
import DemoSection from './components/DemoSection';
import CTASection from './components/CTASection';
import Footer from './components/Footer';
import './App.css';

function App() {
  React.useEffect(() => {
    document.title = 'YourBrand | Tagline';
  }, []);

  return (
    <div className="min-h-screen font-sans bg-white text-gray-900">
      <Navbar />
      <main>
        <HeroSection />
        <FeatureSection />
        <HowItWorksSection />
        <UseCasesSection />
        <TestimonialsSection />
        <PricingSection />
        <DemoSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}

export default App;
```

---

## Phase 10: Design System Guidelines

### 10.1 Color Palette

Choose a consistent color scheme:

```javascript
// Primary: Blue/Indigo scale
'blue-900': '#1e3a8a',
'blue-800': '#1e40af',
'blue-700': '#1d4ed8',
'blue-50': '#eff6ff',

// Secondary: Teal/Green
'teal-600': '#0d9488',
'teal-700': '#0f766e',

// Accent: Indigo for highlights
'indigo-700': '#4338ca',
'indigo-100': '#e0e7ff',

// Neutrals
'gray-900': '#111827',
'gray-700': '#374151',
'gray-600': '#4b5563',
'gray-200': '#e5e7eb',
'gray-50': '#f9fafb',
```

### 10.2 Typography Scale

```javascript
// Headlines
'text-3xl': 30px
'text-4xl': 36px
'text-5xl': 48px

// Body
'text-base': 16px
'text-lg': 18px
'text-xl': 20px

// Small
'text-sm': 14px
```

### 10.3 Spacing System

Use Tailwind's spacing scale consistently:

```
p-4: 16px padding
p-6: 24px padding
p-8: 32px padding
py-24: 96px vertical padding (section spacing)
```

### 10.4 Responsive Breakpoints

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

**Mobile-first approach:**

```jsx
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4"
```

---

## Phase 11: Content Guidelines

### 11.1 Writing Effective Copy

**Hero Section:**

- Headline: 6-10 words, clear value proposition
- Subheadline: 15-25 words, expand on value
- CTA: Action-oriented verb (e.g., "Start Free Trial")

**Features:**

- Title: 2-5 words
- Description: 15-30 words, focus on benefits not features

**Testimonials:**

- Quote: 30-50 words
- Include specific results or metrics when possible

### 11.2 Image Guidelines

**Sources:**

- Unsplash (<https://unsplash.com>) - Free high-quality photos
- Pexels (<https://pexels.com>) - Free stock photos
- Pravatar (<https://i.pravatar.cc/150?img=1>) - Avatar placeholders

**Dimensions:**

- Hero images: 1920x1080 minimum
- Feature icons: Use Lucide React icons
- Use case images: 800x600 minimum
- Testimonial avatars: 150x150

### 11.3 Icon Selection

From Lucide React library, choose icons that:

- Are simple and recognizable
- Maintain consistent line weight
- Relate clearly to the feature

Common choices:

- Brain: AI/Intelligence
- Zap: Speed/Performance
- Shield: Security/Privacy
- Cloud: Cloud services
- Search: Discovery/Search
- Workflow: Automation

---

## Phase 12: Development Workflow

### 12.1 Daily Development

```bash
# Start development server
npm run dev

# Run in separate terminal for live linting
npm run lint

# Format code
npm run format
```

### 12.2 Before Committing

Git hooks automatically run:

1. ESLint on TypeScript files
2. Prettier on all files
3. Fails commit if errors exist

Fix issues:

```bash
npm run lint
npm run format
```

### 12.3 Building for Production

```bash
npm run build
npm run preview
```

Output in `dist/` folder.

---

## Phase 13: Deployment Options

### 13.1 Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

### 13.2 Netlify

1. Connect GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`

### 13.3 Docker

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:80"
    restart: unless-stopped
```

Deploy:

```bash
docker-compose up -d
```

### 13.4 Static Hosting (S3, GitHub Pages)

Build and upload `dist/` folder contents to:

- AWS S3 + CloudFront
- GitHub Pages
- Azure Static Web Apps

---

## Phase 14: Performance Optimization

### 14.1 Image Optimization

- Use WebP format when possible
- Lazy load images below the fold
- Use responsive images with srcset
- Compress images before uploading

### 14.2 Code Splitting

Vite handles this automatically. For additional optimization:

```typescript
// Lazy load sections
const PricingSection = React.lazy(() => import('./components/PricingSection'));

<React.Suspense fallback={<div>Loading...</div>}>
  <PricingSection />
</React.Suspense>
```

### 14.3 Bundle Analysis

```bash
npm install -D rollup-plugin-visualizer

# Add to vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [react(), visualizer()],
});
```

### 14.4 Accessibility

- Use semantic HTML
- Include alt text for images
- Ensure keyboard navigation works
- Test with screen readers
- Maintain color contrast ratios (WCAG AA)

---

## Phase 15: Testing and Quality Assurance

### 15.1 Manual Testing Checklist

**Functionality:**

- [ ] All navigation links work
- [ ] Forms submit correctly
- [ ] Language switcher works
- [ ] Mobile menu opens/closes
- [ ] Pricing toggle switches plans
- [ ] Use case filters work

**Responsive Design:**

- [ ] Test on mobile (375px width)
- [ ] Test on tablet (768px width)
- [ ] Test on desktop (1440px width)
- [ ] Test on large screens (1920px width)

**Cross-Browser:**

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile Safari
- [ ] Mobile Chrome

**Performance:**

- [ ] Lighthouse score > 90
- [ ] First Contentful Paint < 2s
- [ ] Largest Contentful Paint < 2.5s

### 15.2 Automated Testing (Optional)

Install testing libraries:

```bash
npm install -D @testing-library/react @testing-library/jest-dom vitest
```

---

## Phase 16: Analytics and Tracking

### 16.1 Google Analytics

```html
<!-- Add to index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### 16.2 Event Tracking

Track button clicks:

```typescript
const handleCTAClick = () => {
  if (window.gtag) {
    window.gtag('event', 'cta_click', {
      event_category: 'engagement',
      event_label: 'hero_section',
    });
  }
  // Navigate or submit form
};
```

---

## Phase 17: Maintenance and Updates

### 17.1 Content Updates

To update text:

1. Edit JSON files in `src/i18n/locales/`
2. Rebuild and redeploy

To update features:

1. Edit `src/data/features.ts`
2. Ensure icons are imported in FeatureSection
3. Add translations if using i18n

### 17.2 Dependency Updates

```bash
# Check for outdated packages
npm outdated

# Update packages
npm update

# Major version updates
npx npm-check-updates -u
npm install
```

### 17.3 Security

```bash
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix
```

---

## Phase 18: Customization Guide

### 18.1 Changing Brand Colors

1. Update Button component variant styles
2. Update Navbar colors
3. Update section backgrounds and highlights
4. Update hover states throughout

Use find-replace for color values:

- `blue-900` → your primary color
- `teal-600` → your secondary color
- `indigo-700` → your accent color

### 18.2 Adding New Sections

1. Create component in `src/components/NewSection.tsx`
2. Import in `App.tsx`
3. Add between existing sections
4. Create data file if needed
5. Add translations
6. Update navigation if section needs anchor link

### 18.3 Changing Layout

Modify grid layouts:

```jsx
{/* 2-column to 3-column */}
className="grid md:grid-cols-2 lg:grid-cols-3"

{/* Full width to contained */}
className="max-w-7xl mx-auto"

{/* Increase section padding */}
className="py-32" {/* instead of py-24 */}
```

---

## Phase 19: SEO Optimization

### 19.1 Meta Tags

Update `index.html`:

```html
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- SEO Meta Tags -->
  <title>YourBrand | AI-Powered Solution</title>
  <meta name="description" content="Transform your business with our AI-powered platform" />
  <meta name="keywords" content="AI, automation, business intelligence" />

  <!-- Open Graph -->
  <meta property="og:title" content="YourBrand | AI-Powered Solution" />
  <meta property="og:description" content="Transform your business" />
  <meta property="og:image" content="/og-image.jpg" />
  <meta property="og:url" content="https://yourdomain.com" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="YourBrand" />
  <meta name="twitter:description" content="Transform your business" />
  <meta name="twitter:image" content="/og-image.jpg" />

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
</head>
```

### 19.2 Structured Data

Add JSON-LD for rich snippets:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "YourBrand",
  "applicationCategory": "BusinessApplication",
  "offers": {
    "@type": "Offer",
    "price": "29",
    "priceCurrency": "USD"
  }
}
</script>
```

### 19.3 Sitemap

Create `public/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://yourdomain.com</loc>
    <lastmod>2025-01-01</lastmod>
    <priority>1.0</priority>
  </url>
</urlset>
```

---

## Phase 20: Advanced Features (Optional)

### 20.1 Newsletter Signup Integration

```typescript
const handleNewsletterSignup = async (email: string) => {
  const response = await fetch('https://api.yourdomain.com/newsletter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  return response.json();
};
```

### 20.2 Live Chat Integration

```html
<!-- Add Intercom, Drift, or similar -->
<script>
  // Chat widget code
</script>
```

### 20.3 A/B Testing

Use services like:

- Google Optimize
- Optimizely
- VWO

### 20.4 Animation Libraries

For advanced animations:

```bash
npm install framer-motion
```

```typescript
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

---

## Checklist: Project Completion

### Setup Phase

- [ ] Project initialized with Vite + React + TypeScript
- [ ] All dependencies installed
- [ ] Configuration files created
- [ ] Git initialized with hooks
- [ ] Prettier and ESLint configured

### Development Phase

- [ ] Type definitions created
- [ ] Data files populated
- [ ] i18n configured with 2+ languages
- [ ] All section components created
- [ ] Button component created
- [ ] Custom animations added
- [ ] App.tsx composed with all sections

### Content Phase

- [ ] Brand colors customized
- [ ] Copy written for all sections
- [ ] Images sourced and optimized
- [ ] Icons selected and imported
- [ ] Translations completed

### Quality Assurance

- [ ] Tested on mobile devices
- [ ] Tested on desktop browsers
- [ ] Lighthouse score > 90
- [ ] Forms working correctly
- [ ] Language switcher functional
- [ ] All links working

### Deployment

- [ ] Production build successful
- [ ] Deployed to hosting platform
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Analytics installed

### Post-Launch

- [ ] Meta tags optimized
- [ ] Sitemap created
- [ ] Social sharing tested
- [ ] Performance monitored
- [ ] Feedback collected

---

## Common Pitfalls and Solutions

### Issue: Icons not displaying

**Solution:** Ensure icon names in data match imports in component

```typescript
// data/features.ts
icon: 'BrainIcon'

// components/FeatureSection.tsx
import { Brain as BrainIcon } from 'lucide-react';
const iconComponents = { BrainIcon };
```

### Issue: Tailwind styles not applying

**Solution:** Check tailwind.config.js content array includes all file types

```javascript
content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}']
```

### Issue: Language not changing

**Solution:** Verify i18n initialized before App renders

```typescript
// main.tsx
import './i18n'; // Import BEFORE App
```

### Issue: Mobile menu not closing after navigation

**Solution:** Add onClick handler to close menu

```typescript
<a href="#features" onClick={() => setIsMenuOpen(false)}>
```

### Issue: Build size too large

**Solution:**

- Use dynamic imports for heavy components
- Optimize images
- Remove unused dependencies
- Check bundle analyzer

---

## Resources and Further Reading

### Documentation

- React: <https://react.dev>
- TypeScript: <https://www.typescriptlang.org/docs>
- Vite: <https://vitejs.dev>
- TailwindCSS: <https://tailwindcss.com/docs>
- Lucide Icons: <https://lucide.dev>
- i18next: <https://www.i18next.com>

### Design Inspiration

- Dribbble: <https://dribbble.com> (landing page designs)
- Awwwards: <https://www.awwwards.com>
- Land-book: <https://land-book.com>
- One Page Love: <https://onepagelove.com>

### Tools

- Figma: Design mockups
- Coolors: Color palette generator
- TypeScale: Typography scale generator
- PageSpeed Insights: Performance testing
- BrowserStack: Cross-browser testing

---

## Conclusion

This blueprint provides a complete, production-ready foundation for building modern marketing splash pages. The architecture emphasizes:

1. **Maintainability** - Data-driven approach separates content from code
2. **Scalability** - Easy to add sections, languages, and features
3. **Performance** - Optimized build with modern tooling
4. **Quality** - Automated linting, formatting, and git hooks
5. **Internationalization** - Built-in multi-language support

Follow this blueprint step-by-step to create a professional landing page in 1-2 weeks, even as a solo developer. Customize the components, content, and styling to match your brand while maintaining the robust architecture.

**Next Steps:**

1. Clone this blueprint
2. Customize brand colors and content
3. Build your specific sections
4. Deploy to production
5. Iterate based on user feedback

Good luck building!
