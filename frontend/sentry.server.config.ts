// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NODE_ENV === 'production'
    ? "https://257f39dfe68ccbb28f4606c505dc0d60@o4509417834283008.ingest.de.sentry.io/4509417846734928"
    : undefined,

  // Define how likely traces are sampled. Adjust this value in production, or use tracesSampler for greater control.
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 0,

  // Setting this option to true will print useful information to the console while you're setting up Sentry.
  debug: false,
  
  // Disable Sentry in development to prevent 400 errors
  enabled: process.env.NODE_ENV === 'production',
});
