# Retail AI Advisor - Frontend

A modern Next.js 14 application for AI-powered retail insights and pricing optimization.

## Features

- **Authentication**: Secure login/signup with JWT tokens
- **Product Insights**: AI-powered product recommendations with video advisor
- **Cost-Plus Pricing Calculator**: Interactive pricing tool
- **Analytics Dashboard**: Comprehensive business metrics and charts
- **Responsive Design**: Mobile-first responsive design
- **Real-time Updates**: Live data synchronization
- **TypeScript**: Full TypeScript implementation

## Tech Stack

- **Framework**: Next.js 14.2.3 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context + useReducer
- **Forms**: React Hook Form with Zod validation
- **Charts**: Chart.js with react-chartjs-2
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Color Palette

- **Primary**: #427F8C (dark teal)
- **Secondary**: #73B1BF (medium teal)
- **Accent**: #CECF2F (light blue/cyan)
- **Background**: #F2F2F2 (light gray)
- **Text**: #0D0D0D (black)

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── auth/              # Authentication pages
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # Reusable components
│   │   └── ui/               # UI components
│   ├── contexts/             # React contexts
│   ├── lib/                  # Utilities and API client
│   ├── types/                # TypeScript definitions
│   └── styles/               # Additional styles
├── public/                   # Static assets
├── .env.local               # Environment variables
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind configuration
└── package.json             # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

## Pages

### Authentication
- `/auth/login` - User login
- `/auth/signup` - User registration

### Dashboard
- `/dashboard` - Overview with metrics and charts
- `/dashboard/insights` - Product insights with AI advisor video
- `/dashboard/pricing` - Cost-plus pricing calculator
- `/dashboard/analytics` - Detailed analytics and reports
- `/dashboard/settings` - User and store settings

## Key Components

### Authentication
- JWT token management
- Automatic token refresh
- Protected routes with HOC
- User context provider

### Product Insights
- Filter tabs (All, Underpriced, Overstocked, Hot)
- Product recommendations table
- AI advisor video player
- Real-time data updates

### Pricing Calculator
- Real-time price calculation
- Input validation with Zod
- Calculation breakdown
- Pricing tips and recommendations

### Analytics Dashboard
- Revenue trend charts
- Top products analysis
- Inventory status monitoring
- Performance metrics

## API Integration

The frontend integrates with the backend API for:

- User authentication (`/api/v1/auth/*`)
- Product data (`/api/v1/products/*`)
- Analytics (`/api/v1/analytics/*`)
- Video generation (`/api/v1/videos/*`)
- File uploads (`/api/v1/upload/*`)
- Data synchronization (`/api/v1/sync/*`)

## State Management

### AuthContext
- User authentication state
- Store information
- Login/logout functionality
- Token management

### AppContext
- Product filtering
- Analytics data
- Loading states
- Error handling

## Styling

### Tailwind CSS
- Custom color palette configuration
- Responsive design utilities
- Component-based styling
- Dark mode support (future)

### Custom CSS Classes
- Button variants and sizes
- Form input styles
- Card components
- Loading animations

## Performance Optimizations

- Code splitting with Next.js
- Image optimization
- Lazy loading components
- Debounced search inputs
- Memoized calculations

## Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Focus management
- Semantic HTML

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run start
```

### Azure Static Web Apps
1. Uncomment export configuration in `next.config.js`
2. Build the application:
```bash
npm run build
```
3. Deploy the `out` directory to Azure Static Web Apps

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `Retail AI Advisor` |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | Enable analytics features | `true` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
