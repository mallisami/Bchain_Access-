% Local FALLBACK IEEEtran.cls (preview compilation only; not for submission).
% Lets the unmodified \documentclass[journal,onecolumn]{IEEEtran} paper compile
% where the official IEEEtran is unavailable. Use the real IEEEtran for submission.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{IEEEtran}[2026/01/01 v-fallback preview shim over article]
\DeclareOption{journal}{}\DeclareOption{conference}{}\DeclareOption{technote}{}
\DeclareOption{peerreview}{}\DeclareOption{peerreviewca}{}
\DeclareOption{draftcls}{}\DeclareOption{draftclsnofoot}{}
\DeclareOption{compsoc}{}\DeclareOption{comsoc}{}\DeclareOption{transmag}{}
\DeclareOption{onecolumn}{\PassOptionsToClass{onecolumn}{article}}
\DeclareOption{twocolumn}{\PassOptionsToClass{twocolumn}{article}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[10pt]{article}
\RequirePackage[letterpaper,margin=1in]{geometry}
% IEEE-style Roman section numbers so cross-references read naturally
\renewcommand{\thesection}{\Roman{section}}
\renewcommand{\thesubsection}{\thesection-\Alph{subsection}}
\renewcommand{\thesubsubsection}{\thesubsection\arabic{subsubsection}}
% the IEEE author macros the paper uses
\providecommand{\IEEEoverridecommandlockouts}{}
\newcommand{\IEEEauthorblockN}[1]{\begin{tabular}[t]{@{}c@{}}{\normalsize\bfseries #1}\end{tabular}\par}
\newcommand{\IEEEauthorblockA}[1]{\begin{tabular}[t]{@{}c@{}}{\footnotesize #1}\end{tabular}\par\vspace{5pt}}
% robust title (article's tabular-based \maketitle can't hold the \par author blocks)
\renewcommand\maketitle{\begin{center}%
  {\LARGE\bfseries\@title\par}\vspace{1.0em}%
  {\@author\par}\vspace{0.5em}%
  \end{center}\par\vspace{0.5em}}
% IEEE index-terms environment
\newenvironment{IEEEkeywords}{\par\vspace{0.4\baselineskip}\noindent
  \normalfont\footnotesize\textbf{\textit{Index Terms}}---\ignorespaces}{\par\vspace{0.4\baselineskip}}
% harmless stubs sometimes referenced
\providecommand{\IEEEPARstart}[2]{#1#2}
\providecommand{\IEEEraisesectionheading}[1]{#1}
\endinput
