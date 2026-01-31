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
    
    let offset = clientX - containerRect.left - 18; // 18 is half handle width
    const maxOffset = containerRect.width - 40; // 40 is handle width

    if (offset < 0) offset = 0;
    if (offset > maxOffset) offset = maxOffset;

    setSliderPosition(offset);

    if (offset >= maxOffset - 2) {
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
      className="relative w-full h-10 bg-apple-gray rounded-xl overflow-hidden border border-apple-border select-none"
    >
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`text-[12px] font-bold tracking-tight transition-opacity duration-300 ${
          isDragging || isSuccess ? 'opacity-0' : 'opacity-30 text-black'
        }`}>
          Slide to verify
        </span>
      </div>
      
      <motion.div 
        className="absolute inset-y-0 left-0 bg-apple-blue/10 transition-colors"
        style={{ width: sliderPosition + 36 }}
      />

      <motion.div
        onMouseDown={handleStart}
        onTouchStart={handleStart}
        className={`absolute top-1 left-1 bottom-1 w-8 rounded-lg flex items-center justify-center cursor-grab active:cursor-grabbing transition-all
          ${isSuccess ? 'bg-green-500 shadow-lg shadow-green-500/20' : 'bg-white shadow-sm border border-apple-border'}
        `}
        style={{ x: sliderPosition }}
      >
        {isSuccess ? (
          <Check className="w-4 h-4 text-white" />
        ) : (
          <ChevronRight className={`w-4 h-4 transition-colors ${isDragging ? 'text-apple-blue' : 'text-black/20'}`} />
        )}
      </motion.div>

      {isSuccess && (
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] font-bold text-green-600 uppercase tracking-widest"
        >
          Verified
        </motion.div>
      )}
    </div>
  );
};

export default SliderCaptcha;
