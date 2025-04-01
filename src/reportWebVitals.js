/**
 * Measures and reports web vitals metrics (Core Web Vitals) for the application.
 * 
 * This function can report metrics to an analytics endpoint or console log them.
 * 
 * @param {Function} onPerfEntry - Optional callback function to report metrics.
 * Pass a function like (metric) => console.log(metric) to log metrics,
 * or a function that sends data to your analytics service.
 */
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && typeof onPerfEntry === 'function') {
    // Import web-vitals library lazily to avoid impacting app load time
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      // Cumulative Layout Shift
      getCLS(onPerfEntry);
      
      // First Input Delay
      getFID(onPerfEntry);
      
      // First Contentful Paint
      getFCP(onPerfEntry);
      
      // Largest Contentful Paint
      getLCP(onPerfEntry);
      
      // Time To First Byte
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;