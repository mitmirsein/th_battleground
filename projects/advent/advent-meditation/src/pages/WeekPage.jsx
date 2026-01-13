import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Music, Youtube } from 'lucide-react';
import { adventData } from '../data/content';

const WeekPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const weekId = parseInt(id);
    const weekData = adventData.weeks.find(w => w.id === weekId);

    if (!weekData) {
        return <div className="text-center py-20">Week not found</div>;
    }

    const { title, scripture, content, music } = weekData;

    // Extract YouTube ID for embed
    const getYoutubeId = (url) => {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    };

    const youtubeId = getYoutubeId(music.url);

    return (
        <div className="space-y-12 pb-20">
            {/* Navigation Header */}
            <div className="flex justify-between items-center text-sm text-advent-muted">
                <Link to={weekId === 1 ? "/" : `/week/${weekId - 1}`} className="flex items-center gap-1 hover:text-advent-accent transition-colors">
                    <ChevronLeft className="w-4 h-4" /> 이전
                </Link>
                <span className="uppercase tracking-widest">Week {weekId}</span>
                {weekId < 4 ? (
                    <Link to={`/week/${weekId + 1}`} className="flex items-center gap-1 hover:text-advent-accent transition-colors">
                        다음 <ChevronRight className="w-4 h-4" />
                    </Link>
                ) : (
                    <span className="w-12"></span> // Spacer
                )}
            </div>

            {/* Title Section */}
            <motion.div
                key={`title-${weekId}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-6"
            >
                <h1 className="text-3xl md:text-5xl font-serif font-bold text-advent-text break-keep text-balance leading-tight">
                    {title}
                </h1>
            </motion.div>

            {/* Scripture */}
            <motion.div
                key={`scripture-${weekId}`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="bg-white/5 border border-white/10 p-8 rounded-2xl backdrop-blur-sm text-center relative"
            >
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-advent-accent to-transparent opacity-50" />
                <p className="text-xl font-serif italic mb-4 leading-relaxed">"{scripture.text}"</p>
                <p className="text-sm text-advent-accent uppercase tracking-widest">{scripture.source}</p>
            </motion.div>

            {/* Music Embed */}
            <motion.div
                key={`music-${weekId}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="aspect-video w-full rounded-xl overflow-hidden shadow-2xl border border-white/10"
            >
                <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${youtubeId}`}
                    title={music.title}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                ></iframe>
            </motion.div>

            <div className="text-center text-sm text-advent-muted -mt-8">
                <p className="font-bold text-advent-accent mb-1">{music.title}</p>
                <p className="max-w-2xl mx-auto">{music.description}</p>
            </div>

            {/* Content */}
            <motion.div
                key={`content-${weekId}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="space-y-6 text-lg leading-loose text-advent-text/90 font-light"
            >
                {content.map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                ))}
            </motion.div>

            {/* Footer Navigation */}
            <div className="flex justify-center pt-12 border-t border-white/10">
                {weekId < 4 ? (
                    <Link
                        to={`/week/${weekId + 1}`}
                        className="group px-8 py-3 bg-white/10 hover:bg-advent-accent hover:text-advent-bg text-advent-text rounded-full transition-all flex items-center gap-2"
                    >
                        다음 주차 묵상으로 <ChevronRight className="w-4 h-4" />
                    </Link>
                ) : (
                    <div className="text-center space-y-4">
                        <p className="text-advent-accent font-serif text-xl">대림절 묵상의 여정을 마치셨습니다.</p>
                        <Link
                            to="/"
                            className="inline-block px-8 py-3 bg-white/10 hover:bg-white/20 rounded-full transition-all"
                        >
                            처음으로 돌아가기
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default WeekPage;
