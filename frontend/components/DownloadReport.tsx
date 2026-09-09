'use client';

import React, { useState } from 'react';
import { Download, FileText, Loader2 } from 'lucide-react';
import { getPdfDownloadUrl } from '../lib/api';

interface DownloadReportProps {
  sessionId: string;
  startupName?: string;
}

export default function DownloadReport({ sessionId, startupName }: DownloadReportProps) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = () => {
    setDownloading(true);
    const url = getPdfDownloadUrl(sessionId);
    window.open(url, '_blank');
    setTimeout(() => setDownloading(false), 2000);
  };

  return (
    <button
      onClick={handleDownload}
      disabled={downloading}
      className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-semibold text-sm shadow-xl shadow-rose-950/50 transition-all transform hover:-translate-y-0.5 disabled:opacity-50"
    >
      {downloading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Generating PDF...</span>
        </>
      ) : (
        <>
          <FileText className="w-4 h-4" />
          <span>Download Executive PDF Report</span>
          <Download className="w-4 h-4" />
        </>
      )}
    </button>
  );
}
