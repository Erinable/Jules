# Jules Frontend

Next.js frontend application for the Jules AI Code Generation Platform.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Testing**: Vitest + React Testing Library

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout with navigation
│   ├── page.tsx             # Home page
│   ├── users/               # User management
│   ├── tasks/               # Task management
│   ├── agents/              # Agent configuration
│   ├── executions/          # Execution records
│   ├── code-files/          # Code file browser
│   ├── quality/             # Quality metrics
│   └── health/              # Health check
├── components/              # Reusable UI components
│   ├── Layout.tsx           # Main layout with sidebar
│   ├── DataTable.tsx        # Generic table component
│   ├── LoadingSpinner.tsx   # Loading indicator
│   └── ErrorBoundary.tsx    # Error handling
├── src/
│   ├── types/               # TypeScript type definitions
│   │   ├── user.types.ts
│   │   ├── task.types.ts
│   │   ├── agent.types.ts
│   │   ├── execution.types.ts
│   │   ├── codeFile.types.ts
│   │   ├── quality.types.ts
│   │   └── common.types.ts
│   └── services/            # API service layer
│       ├── apiClient.ts     # Axios configuration
│       ├── userService.ts   # User API
│       ├── taskService.ts   # Task API
│       ├── agentService.ts  # Agent API
│       ├── executionService.ts
│       ├── codeFileService.ts
│       ├── qualityService.ts
│       └── healthService.ts
└── lib/
    └── utils.ts             # Utility functions

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env.local
   ```
   
   Update `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```
   
   The app will be available at http://localhost:3000

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run format` - Format code with Prettier
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate coverage report

## Features

### 1. User Management (`/users`)
- View all users
- Create new users
- Delete users
- Email validation

### 2. Task Management (`/tasks`)
- View all tasks with filters
- Create tasks with priority (0-10)
- Update task status (pending, in_progress, completed, failed)
- Delete tasks

### 3. Agent Configuration (`/agents`)
- View all agents
- Create agents with JSON config
- Toggle active/inactive status
- Delete agents

### 4. Execution Records (`/executions`)
- View execution history
- Filter by task ID
- See execution status and timestamps
- Monitor agent performance

### 5. Code File Browser (`/code-files`)
- Load files by project ID
- View file content
- See file hashes and update times
- Access version history

### 6. Quality Metrics (`/quality`)
- View latest quality metrics
- Track avg complexity
- Monitor maintainability index
- Check security issues
- Review test coverage
- View historical trends

### 7. Health Check (`/health`)
- Overall system health
- Readiness status
- Liveness status
- Auto-refresh every 10 seconds

## API Integration

All pages connect to the FastAPI backend at `http://localhost:8000/api/v1`:

- **Users**: `/users/` (GET, POST, PUT, DELETE)
- **Tasks**: `/tasks/` (GET, POST, PUT, PATCH, DELETE)
- **Agents**: `/agents/` (GET, POST, PUT, DELETE)
- **Executions**: `/executions/` (GET, POST, PATCH, DELETE)
- **Code Files**: `/code-files/` (GET, POST, PUT, DELETE)
- **Quality**: `/quality/` (GET, POST, DELETE)
- **Health**: `/health`, `/health/ready`, `/health/live`

## Development

### Adding a New Page

1. Create page file: `app/new-page/page.tsx`
2. Add route to navigation in `components/Layout.tsx`
3. Create service in `src/services/newService.ts`
4. Define types in `src/types/new.types.ts`

### Type Safety

All API responses are typed using TypeScript interfaces based on backend Pydantic schemas. Update types when backend schemas change.

### Error Handling

- API errors are caught and displayed in red alert boxes
- Network errors are logged to console
- ErrorBoundary catches React errors globally

## Testing

Tests should cover:
- Component rendering
- User interactions
- API calls (mocked)
- Error states
- Loading states

Example test structure:
```typescript
import { render, screen, waitFor } from '@testing-library/react'
import UsersPage from './page'

test('loads and displays users', async () => {
  render(<UsersPage />)
  await waitFor(() => {
    expect(screen.getByText(/Users/i)).toBeInTheDocument()
  })
})
```

## Production Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Start production server:
   ```bash
   npm run start
   ```

3. Or use Docker:
   ```bash
   docker build -t jules-frontend .
   docker run -p 3000:3000 jules-frontend
   ```

## Troubleshooting

### Backend Connection Issues

If you see API errors:
1. Ensure backend is running: `http://localhost:8000/docs`
2. Check CORS configuration in backend
3. Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Type Errors

Run type checking:
```bash
npm run type-check
```

### Build Errors

Clear cache and reinstall:
```bash
rm -rf .next node_modules
npm install
npm run build
```

## Architecture Decisions

- **Next.js App Router**: Chosen for file-based routing and better performance
- **Client Components**: All pages use 'use client' for interactivity
- **Axios**: Centralized API client with interceptors
- **No Server Components**: Simplified architecture for admin dashboard
- **Tailwind CSS**: Utility-first CSS for rapid UI development

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Proprietary - Jules AI Platform
