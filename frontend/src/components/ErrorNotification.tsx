interface ErrorNotificationProps {
  message: string;
  onClose: () => void;
}

export const ErrorNotification = ({ message, onClose }: ErrorNotificationProps) => {
  return (
    <div className="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg shadow-lg flex items-start max-w-md z-50">
      <div className="flex-1">
        <p className="font-semibold">Erreur</p>
        <p className="text-sm">{message}</p>
      </div>
      <button
        onClick={onClose}
        className="ml-4 text-red-700 hover:text-red-900 font-bold text-xl"
      >
        ×
      </button>
    </div>
  );
};
