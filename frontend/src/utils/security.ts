/**
 * 密码强度校验逻辑
 * 长度 >= 12, 含大小写, 数字, 特殊字符
 */
export const validatePasswordStrength = (password: string) => {
  const requirements = [
    { regex: /.{12,}/, label: 'At least 12 characters' },
    { regex: /[A-Z]/, label: 'Uppercase letter' },
    { regex: /[a-z]/, label: 'Lowercase letter' },
    { regex: /[0-9]/, label: 'Number' },
    { regex: /[^A-Za-z0-9]/, label: 'Special character' },
  ];

  return requirements.map(req => ({
    label: req.label,
    met: req.regex.test(password)
  }));
};

export const getPasswordStrengthScore = (password: string): number => {
  const results = validatePasswordStrength(password);
  return (results.filter(r => r.met).length / results.length) * 100;
};

/**
 * XSS 过滤简单实现
 */
export const sanitizeInput = (input: string): string => {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};
