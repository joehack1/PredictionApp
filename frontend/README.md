# Frontend Dashboard - Premier League Analyst Pro

## Overview

React 18 + TypeScript frontend dashboard for viewing Premier League predictions. Modern, responsive design with dark theme and real-time data updates.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Website will be at http://localhost:5173
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx                # React entry point
│   ├── App.tsx                 # Main dashboard component
│   ├── index.css               # Global styles (Tailwind)
│   └── hooks/
│       └── useApi.ts           # Custom React hooks
├── public/
│   └── index.html              # HTML template
├── package.json                # Dependencies
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
└── README.md                   # This file
```

## Dependencies

### Core
- **react** (18.2.0) - UI framework
- **react-dom** (18.2.0) - DOM rendering
- **react-router-dom** (6.20.0) - Routing

### Data & State
- **axios** (1.6.2) - HTTP client
- **@tanstack/react-query** (5.25.0) - Server state
- **zustand** (4.4.0) - Client state

### UI & Styling
- **tailwindcss** (3.4.1) - Utility CSS
- **recharts** (2.10.3) - Charts
- **d3** (7.8.5) - Visualizations

### Development
- **vite** (5.0.0) - Build tool
- **typescript** (5.3.3) - Type safety
- **@vitejs/plugin-react** (4.2.1) - Vite React plugin

## Features

### Dashboard Components
- **Upcoming Matches Panel** - List of next matches with predictions
- **Match Details** - Selected match information
- **Prediction Display** - Win/Draw/Loss probabilities
- **Team Form** - Recent match history
- **Head-to-Head** - Historical matchup data

### Custom Hooks

#### useTeams()
```typescript
const { teams, loading, error } = useTeams();
```

#### useMatches(type)
```typescript
const { matches, loading, error, refetch } = useMatches('upcoming');
```

#### usePrediction(matchId)
```typescript
const { prediction, loading, error } = usePrediction(100);
```

#### useTeamForm(teamId, matches)
```typescript
const { form, loading, error } = useTeamForm(1, 5);
```

## Styling

Uses **Tailwind CSS** utility classes:

```tsx
<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
  <div className="bg-gray-800 p-6 rounded-lg">
    Content
  </div>
</div>
```

### Color Scheme
- **Background**: Dark gray (`bg-gray-900`)
- **Cards**: Medium gray (`bg-gray-800`)
- **Text**: White (`text-white`)
- **Accents**: Blue, Green, Yellow, Red

## Development

### Start Dev Server
```bash
npm run dev

# Server runs at http://localhost:5173
# Auto-reloads on file changes
```

### Build for Production
```bash
npm run build

# Creates optimized build in dist/
```

### Preview Production Build
```bash
npm run preview

# Serves dist/ at http://localhost:4173
```

## API Integration

### Base URL
By default: `http://localhost:8000/api/v1`

Configure via environment:
```
VITE_API_URL=http://your-api-url/api/v1
```

### Example Usage

```typescript
import { useMatches, usePrediction } from './hooks/useApi';

export function MyComponent() {
  const { matches, loading } = useMatches('upcoming');
  const { prediction } = usePrediction(matches[0]?.id);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      {matches.map(match => (
        <div key={match.id}>
          {match.home_team.name} vs {match.away_team.name}
        </div>
      ))}
    </div>
  );
}
```

## Routing (Future)

React Router setup prepared for:
- `/` - Dashboard
- `/teams` - Team list
- `/teams/:id` - Team details
- `/matches/:id` - Match details
- `/predictions` - All predictions
- `/account` - User settings (Phase 2)

## State Management

### Zustand Example
Define global state store:

```typescript
import create from 'zustand';

const useStore = create((set) => ({
  selectedMatch: null,
  setSelectedMatch: (match) => set({ selectedMatch: match }),
}));
```

## Deployment

### Build
```bash
npm run build
```

### Deploy Static Files
Upload `dist/` folder to:
- Vercel
- Netlify
- GitHub Pages
- AWS S3
- Any static hosting

### Environment Variables
Create `.env` or `.env.local`:
```
VITE_API_URL=https://api.your-domain.com/api/v1
```

## Performance

### Optimization Techniques
- React Query for efficient data fetching
- Zustand for lightweight state
- Lazy loading with React.lazy (future)
- Code splitting with Vite
- Image optimization (future)

### Lighthouse Targets
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Accessibility

Features:
- Semantic HTML
- Keyboard navigation (planned)
- Color contrast compliance
- ARIA labels (planned)

## Future Improvements

Phase 2:
- [ ] User authentication UI
- [ ] Advanced charts (D3)
- [ ] Prediction leagues
- [ ] User history tracking
- [ ] Dark/Light theme toggle

Phase 3:
- [ ] Mobile-responsive optimization
- [ ] PWA support
- [ ] Offline caching
- [ ] Push notifications

## Troubleshooting

### Port already in use
```bash
npm run dev -- --port 5174
```

### API connection errors
- Check if backend is running: `http://localhost:8000/docs`
- Verify `VITE_API_URL` environment variable
- Check browser console for CORS errors

### Build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
npm run build
```

## Contributing

1. Create feature branch
2. Make changes
3. Test in dev server
4. Create Pull Request

## License

This project is provided as-is for development and educational purposes.

---

**Last Updated**: February 10, 2026  
**Status**: MVP Phase 1  
**Framework**: React 18 + TypeScript  
**Styling**: Tailwind CSS
