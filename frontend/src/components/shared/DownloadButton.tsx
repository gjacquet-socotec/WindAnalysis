import { Download, FileText, CheckCircle } from 'lucide-react';
import { useState } from 'react';

interface DownloadButtonProps {
  reportPath?: string;
}

export function DownloadButton({ reportPath }: DownloadButtonProps) {
  const [downloaded, setDownloaded] = useState(false);

  if (!reportPath) {
    return (
      <div className="flex items-center justify-center p-4 bg-gray-100 rounded-lg text-gray-500">
        <FileText className="w-5 h-5 mr-2" />
        <span className="text-sm">Aucun rapport disponible</span>
      </div>
    );
  }

  const handleDownload = () => {
    // For now, just show the path (actual download would need backend endpoint)
    console.log('Download report from:', reportPath);
    setDownloaded(true);

    // Reset after 3 seconds
    setTimeout(() => setDownloaded(false), 3000);
  };

  return (
    <div className="flex flex-col items-center space-y-3">
      <button
        onClick={handleDownload}
        disabled={downloaded}
        className="flex items-center space-x-3 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold rounded-lg shadow-md transition-colors"
      >
        {downloaded ? (
          <>
            <CheckCircle className="w-5 h-5" />
            <span>Téléchargé !</span>
          </>
        ) : (
          <>
            <Download className="w-5 h-5" />
            <span>Télécharger le rapport Word</span>
          </>
        )}
      </button>

      <p className="text-xs text-gray-500 text-center max-w-md break-all">
        {reportPath}
      </p>
    </div>
  );
}
