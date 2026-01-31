import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      "welcome": "Orchestrate Artistic Intents.",
      "engine": "Engine",
      "audit": "Audit Traces",
      "balance": "Balance",
      "execute": "Execute Runtime",
      "refill_soon": "Refill coming soon",
      "sign_out": "Sign Out"
    }
  },
  zh: {
    translation: {
      "welcome": "编排艺术意图。",
      "engine": "引擎",
      "audit": "审计追踪",
      "balance": "余额",
      "execute": "执行运行时",
      "refill_soon": "充值功能即将推出",
      "sign_out": "退出登录"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
