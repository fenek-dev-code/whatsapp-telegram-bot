import { makeWASocket, useMultiFileAuthState, DisconnectReason } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import path from 'path';
import { fileURLToPath } from 'url';
import { findMatch } from './validation.js';
import dotenv from 'dotenv'; // Загружает переменные из .env
dotenv.config();

const api_secret = "secret";
const allowedChats = process.env.WHATSAPP_ALLOWED_CHATS.split(',');
const on_chats = process.env.WHATSAPP_ON_CHATS.toLowerCase();


// 1. Получаем __dirname в ES-модулях
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 2. Настройка аутентификации
const { state, saveCreds } = await useMultiFileAuthState(path.join(__dirname, 'auth'));

// 3. Создание бота
const startBot = async () => {
    const sock = makeWASocket({
        auth: state,
        browser: ['MyBot', 'Chrome', '1.0'],
        markOnlineOnConnect: true,
    });

    // 4. Динамический импорт qrcode-terminal
    let qrcode;
    try {
        const qrModule = await import('qrcode-terminal');
        qrcode = qrModule.default;
    } catch (err) {
        console.error('⚠️ Не удалось загрузить qrcode-terminal:', err);
        process.exit(1);
    }

    // 5. Обработка подключения и QR-кода
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;  
        if (qr) {
            console.log('🔍 Отсканируйте QR-код:');
            qrcode.generate(qr, { small: true });
        }
        
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect.error instanceof Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('🔁 Переподключение...', shouldReconnect);
            if (shouldReconnect) startBot();
        } else if (connection === 'open') {
            console.log('✅ Бот подключен к WhatsApp!');
        }
    });

    // 6. Сохранение сессии
    sock.ev.on('creds.update', saveCreds);

    // 7. Обработка сообщений
    sock.ev.on('messages.upsert', async ({ messages }) => {
        const msg = messages[0];
        if (!allowedChats.includes(msg.key.remoteJid)){
            if (on_chats == "false") {
                return
            }
        };

        const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
        if (text.toLowerCase() === '!chat_id') {
            await sock.sendMessage(msg.key.remoteJid, { text: `ID чата: ${msg.key.remoteJid}` });
        }
        if (!msg.key.fromMe) {
            const number = msg.key.participant?.split('@')[0] || 'Без номера';
            await send_message_bot(text, number);
            console.log(`📩[${number}]: ${text}`);
            const category = findMatch(text);
            if (category !== null) {
                await send_message_bot(text, number, category);
            }
        }
    });

    return sock;
};

// 8. Запуск бота
try {
    const sock = await startBot();
    console.log('🤖 Бот успешно инициализирован');
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
        console.log('🛑 Остановка бота...');
        await sock.end();
        process.exit(0);
    });
} catch (err) {
    console.error('🚨 Ошибка запуска:', err);
    process.exit(1);
}


async function send_message_bot(text, number, category) {
    fetch(`http://localhost:8080/webhook/whatsapp/${api_secret}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "text":text,
            "number":number,
            "category":category
        }),
    })
}