import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Check } from 'lucide-react';

interface SliderCaptchaProps {
  onSuccess: () => void;
}

const SliderCaptcha: React.FC<SliderCaptchaProps> = ({ onSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [sliderPosition, setSliderPosition] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleStart = () => {
    if (isSuccess) return;
    setIsDragging(true);
  };

  const handleMove = (e: MouseEvent | TouchEvent) => {
    if (!isDragging || isSuccess || !containerRef.current) return;

    const container = containerRef.current;
    const containerRect = container.getBoundingClientRect();
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    
    let offset = clientX - containerRect.left - 20; // 20 is half handle width
    const maxOffset = containerRect.width - 44; // 44 is handle width

    if (offset < 0) offset = 0;
    if (offset > maxOffset) offset = maxOffset;

    setSliderPosition(offset);

    if (offset >= maxOffset - 5) {
      setIsSuccess(true);
      setIsDragging(false);
      onSuccess();
    }
  };

  const handleEnd = () => {
    if (!isSuccess) {
      setIsDragging(false);
      setSliderPosition(0);
    }
  };

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMove);
      window.addEventListener('mouseup', handleEnd);
      window.addEventListener('touchmove', handleMove);
      window.addEventListener('touchend', handleEnd);
    } else {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleEnd);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleEnd);
    }
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleEnd);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleEnd);
    };
  }, [isDragging]);

  return (
    <div 
      ref={containerRef}
      className="relative w-full h-11 bg-apple-gray rounded-xl overflow-hidden border border-apple-border select-none"
    >
      <div className="absolute inset-0 flex items-center justify-center text-[13px] font-medium text-black/30">
        {isSuccess ? 'Verified' : 'Slide to verify'}
      </div>
      
      <motion.div 
        className="absolute inset-y-0 left-0 bg-apple-blue/10"
        style={{ width: sliderPosition + 44 }}
      />

      <motion.div
        onMouseDown={handleStart}
        onTouchStart={handleStart}
        className={`absolute top-1 left-1 bottom-1 w-9 rounded-lg flex items-center justify-center cursor-grab active:cursor-grabbing transition-colors
          ${isSuccess ? 'bg-green-500' : 'bg-white shadow-sm border border-apple-border'}
        `}
        style={{ x: sliderPosition }}
      >
        {isSuccess ? (
          <Check className="w-5 h-5 text-white" />
        ) : (
          <ChevronRight className={`w-5 h-5 ${isDragging ? 'text-apple-blue' : 'text-black/20'}`} />
        )}
      </motion.div>
    </div>
  );
};

export default SliderCaptcha;
