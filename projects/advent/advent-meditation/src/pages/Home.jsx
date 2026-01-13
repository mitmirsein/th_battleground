import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Music } from 'lucide-react';
import { adventData } from '../data/content';

const Home = () => {
    const { title, subtitle, scripture, content, music } = adventData.intro;

    return (
        <div className="space-y-12">
            {/* Header Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-center space-y-6"
            >
                <h1 className="text-4xl md:text-6xl font-serif font-bold text-transparent bg-clip-text bg-gradient-to-r from-advent-text via-advent-accent to-advent-text pb-2 break-keep text-balance leading-tight">
                    {title}
                </h1>
                <p className="text-xl text-advent-muted font-light tracking-wide">{subtitle}</p>
            </motion.div>

            {/* Scripture Quote */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="bg-white/5 border border-white/10 p-8 rounded-2xl backdrop-blur-sm text-center relative overflow-hidden"
            >
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-advent-accent to-transparent opacity-50" />
                <p className="text-2xl font-serif italic mb-4 leading-relaxed">"{scripture.text}"</p>
                <p className="text-sm text-advent-accent uppercase tracking-widest">{scripture.source}</p>
            </motion.div>

            {/* Main Content */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="space-y-6 text-lg leading-loose text-advent-text/90 font-light"
            >
                {content.map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                ))}
            </motion.div>

            {/* Music Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="space-y-4"
            >
                <div className="flex items-center gap-3 text-advent-accent mb-4">
                    <Music className="w-6 h-6" />
                    <h3 className="text-xl font-bold font-serif">묵상의 시작을 여는 음악</h3>
                </div>

                <div className="aspect-video w-full rounded-xl overflow-hidden shadow-2xl border border-white/10 bg-black">
                    <iframe
                        width="100%"
                        height="100%"
                        src={`https://www.youtube.com/embed/${music.url.split('v=')[1]}`}
                        title={music.title}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                    ></iframe>
                </div>

                <div className="text-center md:text-left space-y-2">
                    <p className="font-bold text-lg">{music.title}</p>
                    <p className="text-sm text-advent-muted leading-relaxed">{music.description}</p>
                </div>
            </motion.div>

            {/* CTA Button */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 }}
                className="flex justify-center pt-8"
            >
                <Link
                    to="/week/1"
                    className="group relative px-8 py-4 bg-advent-accent text-advent-bg font-bold text-lg rounded-full overflow-hidden transition-transform hover:scale-105"
                >
                    <span className="relative z-10 flex items-center gap-2">
                        여정 시작하기 <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </span>
                    <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                </Link>
            </motion.div>
        </div>
    );
};

export default Home;
