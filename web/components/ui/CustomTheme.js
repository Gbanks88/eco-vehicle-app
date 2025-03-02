import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState({
    mode: 'light',
    color: 'blue',
    radius: 'medium',
    animation: true
  });

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('ui-theme');
    if (savedTheme) {
      setTheme(JSON.parse(savedTheme));
    }

    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme.mode);
    document.documentElement.setAttribute('data-color', theme.color);
    document.documentElement.setAttribute('data-radius', theme.radius);
    document.documentElement.setAttribute('data-animation', theme.animation);
  }, [theme]);

  const updateTheme = (newTheme) => {
    const updatedTheme = { ...theme, ...newTheme };
    setTheme(updatedTheme);
    localStorage.setItem('ui-theme', JSON.stringify(updatedTheme));
  };

  return (
    <ThemeContext.Provider value={{ theme, updateTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// Theme configuration
export const themeConfig = {
  modes: ['light', 'dark', 'system'],
  colors: ['blue', 'green', 'purple', 'orange', 'red'],
  radius: ['none', 'small', 'medium', 'large', 'full'],
  animations: {
    none: 'none',
    fast: '100ms',
    normal: '200ms',
    slow: '300ms'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem'
  },
  typography: {
    fonts: {
      sans: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif',
      mono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace'
    },
    sizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem'
    },
    weights: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    }
  },
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
  }
};
