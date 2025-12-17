import { type ReactNode } from "react";

type Props = {
  title?: string;
  actions?: ReactNode;
  children: ReactNode;
};

const Card = ({ title, actions, children }: Props) => (
  <section className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
    {(title || actions) && (
      <header className="flex items-center justify-between gap-3 mb-3">
        {title && (
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        )}
        {actions && <div className="flex gap-2">{actions}</div>}
      </header>
    )}
    <div>{children}</div>
  </section>
);

export default Card;
