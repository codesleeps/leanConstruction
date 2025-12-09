import React from 'react';
import { Box, Typography } from '@mui/material';
import { Construction } from '@mui/icons-material';

const Logo = ({ size = 'medium', variant = 'full', sx = {} }) => {
  const sizes = {
    small: { iconSize: 24, fontSize: '1.2rem', iconBox: 40 },
    medium: { iconSize: 40, fontSize: '1.5rem', iconBox: 60 },
    large: { iconSize: 60, fontSize: '2rem', iconBox: 80 },
    xl: { iconSize: 80, fontSize: '2.5rem', iconBox: 100 }
  };

  const { iconSize, fontSize, iconBox } = sizes[size] || sizes.medium;

  if (variant === 'icon') {
    return (
      <Box
        sx={{
          width: iconBox,
          height: iconBox,
          borderRadius: '16px',
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(25, 118, 210, 0.3)',
          ...sx
        }}
      >
        <Construction sx={{ fontSize: iconSize, color: 'white' }} />
      </Box>
    );
  }

  if (variant === 'text') {
    return (
      <Typography
        variant="h4"
        fontWeight="bold"
        sx={{
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          ...sx
        }}
      >
        Lean Construction AI
      </Typography>
    );
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', ...sx }}>
      <Box
        sx={{
          width: iconBox,
          height: iconBox,
          borderRadius: '16px',
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mr: 2,
          boxShadow: '0 4px 20px rgba(25, 118, 210, 0.3)'
        }}
      >
        <Construction sx={{ fontSize: iconSize, color: 'white' }} />
      </Box>
      <Typography
        variant="h4"
        fontWeight="bold"
        sx={{
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}
      >
        Lean Construction AI
      </Typography>
    </Box>
  );
};

export default Logo;