import { useState } from 'react';
import { useTheme, themeConfig } from './CustomTheme';

export default function ThemeCustomizer() {
  const { theme, updateTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const handleModeChange = (mode) => {
    updateTheme({ mode });
  };

  const handleColorChange = (color) => {
    updateTheme({ color });
  };

  const handleRadiusChange = (radius) => {
    updateTheme({ radius });
  };

  const handleAnimationToggle = () => {
    updateTheme({ animation: !theme.animation });
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${isOpen ? 'w-80' : 'w-auto'}`}>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-12 h-12 rounded-full shadow-lg flex items-center justify-center
          ${theme.mode === 'dark'
            ? 'bg-gray-800 text-white hover:bg-gray-700'
            : 'bg-white text-gray-800 hover:bg-gray-50'
          } transition-colors`}
      >
        <svg
          className="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d={isOpen
              ? 'M6 18L18 6M6 6l12 12'
              : 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4'
            }
          />
        </svg>
      </button>

      {/* Customizer Panel */}
      {isOpen && (
        <div className={`mt-4 p-6 rounded-lg shadow-xl
          ${theme.mode === 'dark'
            ? 'bg-gray-800 text-white'
            : 'bg-white text-gray-800'
          }`}
        >
          <h3 className="text-lg font-semibold mb-4">Customize Theme</h3>

          {/* Mode Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Mode</label>
            <div className="grid grid-cols-3 gap-2">
              {themeConfig.modes.map(mode => (
                <button
                  key={mode}
                  onClick={() => handleModeChange(mode)}
                  className={`px-3 py-2 rounded text-sm capitalize
                    ${theme.mode === mode
                      ? 'bg-blue-500 text-white'
                      : theme.mode === 'dark'
                        ? 'bg-gray-700 hover:bg-gray-600'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          {/* Color Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Color</label>
            <div className="grid grid-cols-5 gap-2">
              {themeConfig.colors.map(color => (
                <button
                  key={color}
                  onClick={() => handleColorChange(color)}
                  className={`w-8 h-8 rounded-full border-2
                    ${theme.color === color
                      ? 'border-blue-500'
                      : 'border-transparent'
                    } bg-${color}-500 hover:opacity-80 transition-opacity`}
                  title={color}
                />
              ))}
            </div>
          </div>

          {/* Border Radius */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Border Radius</label>
            <div className="grid grid-cols-3 gap-2">
              {themeConfig.radius.map(radius => (
                <button
                  key={radius}
                  onClick={() => handleRadiusChange(radius)}
                  className={`px-3 py-2 rounded text-sm capitalize
                    ${theme.radius === radius
                      ? 'bg-blue-500 text-white'
                      : theme.mode === 'dark'
                        ? 'bg-gray-700 hover:bg-gray-600'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                >
                  {radius}
                </button>
              ))}
            </div>
          </div>

          {/* Animation Toggle */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={theme.animation}
                onChange={handleAnimationToggle}
                className="form-checkbox h-5 w-5 text-blue-500"
              />
              <span className="ml-2 text-sm">Enable animations</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
