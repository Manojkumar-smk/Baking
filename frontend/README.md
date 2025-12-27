# Cookie Shop Frontend

React + TypeScript frontend for the Cookie Shop e-commerce platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Stripe** - Payment processing
- **React Hook Form** - Form management
- **Zod** - Schema validation

## Getting Started

### Install Dependencies

```bash
npm install
```

### Environment Variables

Copy `.env.example` to `.env.development`:

```bash
cp .env.example .env.development
```

Update the values:

```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_key
```

### Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── assets/           # Static assets (images, styles)
├── components/       # Reusable UI components
│   ├── common/      # Common components (Button, Input, etc.)
│   ├── auth/        # Authentication components
│   ├── products/    # Product-related components
│   ├── cart/        # Shopping cart components
│   ├── checkout/    # Checkout flow components
│   └── admin/       # Admin dashboard components
├── pages/           # Page components
├── contexts/        # React Context providers
├── hooks/           # Custom React hooks
├── services/        # API service layers
├── types/           # TypeScript type definitions
├── utils/           # Utility functions
└── routes/          # Routing configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Path Aliases

The project uses path aliases for cleaner imports:

```typescript
import Button from '@components/common/Button'
import { useAuth } from '@hooks/useAuth'
import { User } from '@types/user.types'
```

Available aliases:
- `@/` - src directory
- `@components/` - components directory
- `@pages/` - pages directory
- `@services/` - services directory
- `@hooks/` - hooks directory
- `@types/` - types directory
- `@utils/` - utils directory
- `@contexts/` - contexts directory
- `@assets/` - assets directory
